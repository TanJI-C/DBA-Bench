# Query business data on the secondary cluster with Syncpoint

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dr-secondary-cluster.md`
- Source Title: `DR Solution Based on Primary and Secondary Clusters`
- Source Heading Path: `DR Solution Based on Primary and Secondary Clusters > Set up primary and secondary clusters based on TiCDC > Query business data on the secondary cluster`
- Source Line Ranges: `376-410`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `secondary-read`, `syncpoint`, `external-ts`, `changefeed`, `consistent-snapshot`, `redo-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0096_505a11b2ee`
- Source ID: `tidb-docs-8.1:dr-secondary-cluster.md#query-business-data-on-the-secondary-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cb2d992cfe805d4cfa88c1afa67e240d4d94ccc9f7da5dddf13a349c46bd927f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dr-secondary-cluster#query-business-data-on-the-secondary-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dr-secondary-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when asking how to query transactionally consistent business data on the secondary cluster by enabling Syncpoint and external timestamp reads.
- Retrieval Keywords: Query business data on the secondary cluster, Syncpoint, enable-sync-point, sync-point-interval, sync-point-retention, SET GLOBAL tidb_external_ts = @@tidb_current_ts, SET GLOBAL|SESSION tidb_enable_external_ts_read = ON, tidb_enable_external_ts_read, tidb_external_ts, changefeed, SYSTEM_VARIABLES_ADMIN, SUPER, redo logs, [consistent], level = "eventual", max-log-size, flush-interval, storage = "s3://redo", secondary cluster can only replicate data from one changefeed
- Follow-up Guidance: The source states that when creating the changefeed you enable Syncpoint in the configuration file, and the business application enables external timestamp reads to query consistent data from the secondary cluster.
- Classification Note: This is classified as configuration because the content centers on changefeed and session or global settings such as enable-sync-point, sync-point-interval, sync-point-retention, and tidb_enable_external_ts_read.

## Official Source Content

### Query business data on the secondary cluster

In a primary-secondary DR scenario, it is common that the secondary cluster is used as a read-only cluster to run some latency-insensitive queries. TiDB also provides this feature by its primary-secondary DR solution.

When creating the changefeed, enable the Syncpoint feature in the configuration file. Then the changefeed periodically (at `sync-point-interval`) sets the consistent snapshot point that has been replicated to the secondary cluster by executing `SET GLOBAL tidb_external_ts = @@tidb_current_ts` on the secondary cluster.

To query data from the secondary cluster, configure `SET GLOBAL|SESSION tidb_enable_external_ts_read = ON;` in the business application. Then you can get the data that is transactionally consistent with the primary cluster.

```toml
# Starting from v6.4.0, only the changefeed with the SYSTEM_VARIABLES_ADMIN or SUPER privilege can use the TiCDC Syncpoint feature.
enable-sync-point = true

# Specifies the interval at which Syncpoint aligns the primary and secondary snapshots. It also indicates the maximum latency at which you can read the complete transaction, for example, read the transaction data generated on the primary cluster two minutes ago from the secondary cluster.
# The format is in h m s. For example, "1h30m30s". The default value is "10m" and the minimum value is "30s".
sync-point-interval = "10m"

# Specifies how long the data is retained by Syncpoint in the downstream table. When this duration is exceeded, the data is cleaned up.
# The format is in h m s. For example, "24h30m30s". The default value is "24h".
sync-point-retention = "1h"

[consistent]
# eventual consistency: redo logs are used to ensure eventual consistency in disaster scenarios.
level = "eventual"
# The size of a single redo log, in MiB. The default value is 64, and the recommended value is less than 128.
max-log-size = 64
# Interval for refreshing or uploading redo logs to Amazon S3, in milliseconds. The default value is 1000, and the recommended value range is 500-2000.
flush-interval = 2000
# The path where redo logs are saved.
storage = "s3://redo?access-key=minio&secret-access-key=miniostorage&endpoint=http://10.0.1.10:6060&force-path-style=true"
```

> **Note:**
>
> In a primary-secondary DR architecture, a secondary cluster can only replicate data from one changefeed. Otherwise, the data transaction integrity of the secondary cluster cannot be guaranteed.
