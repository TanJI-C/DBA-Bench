# Validate upstream and downstream data with ts-map snapshots

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-upstream-downstream-check.md`
- Source Title: `Upstream and Downstream Clusters Data Validation and Snapshot Read`
- Source Heading Path: `Upstream and Downstream Clusters Data Validation and Snapshot Read > Data consistency validation | Upstream and Downstream Clusters Data Validation and Snapshot Read > Data consistency validation > Step 1: obtain `ts-map` | Upstream and Downstream Clusters Data Validation and Snapshot Read > Data consistency validation > Step 2: configure snapshot | Upstream and Downstream Clusters Data Validation and Snapshot Read > Notes`
- Source Line Ranges: `44-100`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`, `tikv`, `shared`
- Topic Tags: `data-validation`, `sync-diff-inspector`, `snapshot`, `ts-map`, `gc`, `privileges`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0075_ea9c8900d4`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-upstream-downstream-check.md#data-consistency-validation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `99c013e4921d8b28343b372370d87c97c7ad4761fb9487b4d0391da9cdb1c2a1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-upstream-downstream-check#data-consistency-validation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-upstream-downstream-check.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact ts-map fields and snapshot configuration needed to validate upstream and downstream data with sync-diff-inspector.
- Retrieval Keywords: data consistency validation, sync-diff-inspector, snapshot, select * from tidb_cdc.syncpoint_v1, primary_ts, secondary_ts, ticdc_cluster_id, changefeed, Datasource config, data-sources.uptidb, data-sources.downtidb, GC time of TiKV, SYSTEM_VARIABLES_ADMIN, SUPER
- Follow-up Guidance: The notes state that data validation with Syncpoint requires preserving historical snapshot data from TiKV GC during the check and that, since v6.4.0, only a changefeed with the SYSTEM_VARIABLES_ADMIN or SUPER privilege can use the TiCDC Syncpoint feature.
- Classification Note: This is classified as a diagnosis chunk because the content focuses on validating data consistency by obtaining ts-map records and configuring snapshot points for comparison.

## Official Source Content

## Data consistency validation

> **Note:**
>
> Before you perform data consistency validation, make sure that you have [enabled the Syncpoint feature](#enable-syncpoint).

To validate the data of upstream and downstream clusters, you only need to configure `snapshot` in sync-diff-inspector.
### Step 1: obtain `ts-map`

You can execute the following SQL statement in the downstream TiDB cluster to obtain the upstream TSO (`primary_ts`) and downstream TSO (`secondary_ts`):

```sql
select * from tidb_cdc.syncpoint_v1;
+------------------+----------------+--------------------+--------------------+---------------------+
| ticdc_cluster_id | changefeed     | primary_ts         | secondary_ts       | created_at          |
+------------------+----------------+--------------------+--------------------+---------------------+
| default          | test-2 | 435953225454059520 | 435953235516456963 | 2022-09-13 08:40:15 |
+------------------+----------------+--------------------+--------------------+---------------------+
```

The fields in the preceding `syncpoint_v1` table are described as follows:

- `ticdc_cluster_id`: The ID of the TiCDC cluster in this record.
- `changefeed`: The ID of the changefeed in this record. Because different TiCDC clusters might have changefeeds with the same name, you need to confirm the `ts-map` inserted by a changefeed with the TiCDC cluster ID and changefeed ID.
- `primary_ts`: The timestamp of the upstream database snapshot.
- `secondary_ts`: The timestamp of the downstream database snapshot.
- `created_at`: The time when this record is inserted.
### Step 2: configure snapshot

Then configure the snapshot information of the upstream and downstream databases by using the `ts-map` information obtained in [Step 1](#step-1-obtain-ts-map).

Here is a configuration example of the `Datasource config` section:

```toml
######################### Datasource config ########################
[data-sources.uptidb]
    host = "172.16.0.1"
    port = 4000
    user = "root"
    password = ""
    snapshot = "435953225454059520"

[data-sources.downtidb]
    host = "172.16.0.2"
    port = 4000
    user = "root"
    snapshot = "435953235516456963"
```
## Notes

- Before TiCDC creates a changefeed, make sure that the value of the TiCDC configuration item `enable-sync-point` is set to `true`. Only in this way, Syncpoint is enabled and the `ts-map` is saved in the downstream. For the complete configuration, see [TiCDC task configuration file](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config).
- When you perform data validation using Syncpoint, you need to modify the Garbage Collection (GC) time of TiKV to ensure that the historical data corresponding to snapshot is not collected by GC during the data check. It is recommended that you modify the GC time to 1 hour and recover the setting after the check.
- The above example only shows the section of `Datasource config`. For complete configuration, refer to [sync-diff-inspector User Guide](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview).
- Since v6.4.0, only the changefeed with the `SYSTEM_VARIABLES_ADMIN` or `SUPER` privilege can use the TiCDC Syncpoint feature.
