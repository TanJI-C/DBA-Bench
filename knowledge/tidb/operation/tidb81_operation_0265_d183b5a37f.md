# Enable Syncpoint and perform consistent snapshot reads

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-upstream-downstream-check.md`
- Source Title: `Upstream and Downstream Clusters Data Validation and Snapshot Read`
- Source Heading Path: `Upstream and Downstream Clusters Data Validation and Snapshot Read | Upstream and Downstream Clusters Data Validation and Snapshot Read > Enable Syncpoint | Upstream and Downstream Clusters Data Validation and Snapshot Read > Consistent snapshot read`
- Source Line Ranges: `5-43`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`, `sql`
- Topic Tags: `syncpoint`, `snapshot-read`, `replication`, `ts-map`, `changefeed`, `external-ts`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0265_d183b5a37f`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-upstream-downstream-check.md#upstream-and-downstream-clusters-data-validation-and-snapshot-read`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8f19c2339939e316b296f1d0ab05632df3e74fcc745831fee883bfa9b95ae268`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-upstream-downstream-check#upstream-and-downstream-clusters-data-validation-and-snapshot-read
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-upstream-downstream-check.md

## Retrieval Guidance

- Use When: Use this chunk when you need to understand how TiCDC Syncpoint enables consistent snapshot reads between upstream and downstream TiDB clusters during replication.
- Retrieval Keywords: TiCDC Syncpoint, enable-sync-point, sync-point-interval, sync-point-retention, tidb_cdc.syncpoint_v1, ts-map, SET GLOBAL tidb_external_ts = @@tidb_current_ts, SET GLOBAL|SESSION tidb_enable_external_ts_read = ON, consistent snapshot read, tidb_external_ts, changefeed
- Follow-up Guidance: If multiple replication tasks use the same downstream TiDB cluster, consistent snapshot read needs to be set up at the replication task level by reading records from the ts-map table.
- Classification Note: This is classified as an operation chunk because the content explains enabling the Syncpoint feature and using it for consistent snapshot read during replication.

## Official Source Content

# Upstream and Downstream Clusters Data Validation and Snapshot Read

When you use TiCDC to build upstream and downstream clusters of TiDB, you might need to perform consistent snapshot read or data consistency validation on the upstream and downstream without stopping the replication. In the regular replication mode, TiCDC only guarantees that the data is eventually consistent, but cannot guarantee that the data is consistent during the replication process. Therefore, it is difficult to perform consistent read of dynamically changing data. To meet such a need, TiCDC provides the Syncpoint feature.

Syncpoint uses the snapshot feature provided by TiDB and enables TiCDC to maintain a `ts-map` that has consistency between upstream and downstream snapshots during the replication process. In this way, the issue of verifying the consistency of dynamic data is converted to the issue of verifying the consistency of static snapshot data, which achieves the effect of nearly real-time verification.
## Enable Syncpoint

After enabling the Syncpoint feature, you can use [Consistent snapshot read](#consistent-snapshot-read) and [Data consistency validation](#data-consistency-validation).

To enable the Syncpoint feature, set the value of the TiCDC configuration item `enable-sync-point` to `true` when creating a replication task. After enabling Syncpoint, TiCDC writes the following information to the downstream TiDB cluster:

1. During the replication, TiCDC periodically (configured by `sync-point-interval`) aligns snapshots between the upstream and downstream and saves the upstream and downstream TSO correspondences in the downstream `tidb_cdc.syncpoint_v1` table.
2. During the replication, TiCDC also periodically (configured by `sync-point-interval`) executes `SET GLOBAL tidb_external_ts = @@tidb_current_ts`, which sets a consistent snapshot point that has been replicated in backup clusters.

The following TiCDC configuration example enables Syncpoint when creating a replication task:

```toml
# Enables SyncPoint.
enable-sync-point = true

# Aligns the upstream and downstream snapshots every 5 minutes
sync-point-interval = "5m"

# Cleans up the ts-map data in the downstream tidb_cdc.syncpoint_v1 table every hour
sync-point-retention = "1h"
```
## Consistent snapshot read

> **Note:**
>
> Before you perform consistent snapshot read, make sure that you have [enabled the Syncpoint feature](#enable-syncpoint). If multiple replication tasks use the same downstream TiDB cluster and have Syncpoint enabled, each of these tasks updates `tidb_external_ts` and `ts-map` based on their respective replication progress. In this case, you need to set up consistent snapshot read at the replication task level by reading records from the `ts-map` table. Meanwhile, you need to avoid downstream applications reading data using `tidb_enable_external_ts_read`, because multiple replication tasks might interfere with each other and result in inconsistent results.

When you need to query the data from the backup cluster, you can set `SET GLOBAL|SESSION tidb_enable_external_ts_read = ON;` for the application to obtain transactionally consistent data on the backup cluster.

In addition, you can also select a previous point in time for snapshot read by querying `ts-map`.
