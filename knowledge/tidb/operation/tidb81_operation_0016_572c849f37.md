# BR checkpoint backup overview, mechanism, and limitations

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-checkpoint-backup.md`
- Source Title: `Checkpoint Backup`
- Source Heading Path: `Checkpoint Backup | Checkpoint Backup > Application scenarios | Checkpoint Backup > Implementation details | Checkpoint Backup > Usage limitations | Checkpoint Backup > Usage limitations > Backup retry must be prior to GC | Checkpoint Backup > Usage limitations > Some data needs to be backed up again`
- Source Line Ranges: `5-52`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `tikv`
- Topic Tags: `checkpoint-backup`, `snapshot-backup`, `interrupted-backup`, `backup-retry`, `gc-safepoint`, `gcttl`, `external-storage`, `key-ranges`, `retention-period`, `data-rebackup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0016_572c849f37`
- Source ID: `tidb-docs-8.1:br/br-checkpoint-backup.md#checkpoint-backup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0aae7230754cf296013a3493df17424611659e695f409509c654056d6fe92443`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-checkpoint-backup#checkpoint-backup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-checkpoint-backup.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about BR checkpoint backup for interrupted snapshot backup, how retry resumes from recorded key ranges, or what limitations apply around GC and re-backing up data.
- Retrieval Keywords: Checkpoint Backup, BR checkpoint backup, snapshot backup interrupted, continue an interrupted backup, backup retry, br command-line tool, key ranges, external storage, gc-safepoint, gcttl, retention period, Backup retry must be prior to GC, Some data needs to be backed up again, tiup br backup full --gcttl 54000
- Follow-up Guidance: The source also states that `br` keeps the `gc-safepoint` for about one hour by default when `gcttl` is not specified, and shows `tiup br backup full --storage local:///br_data/ --pd "${PD_IP}:2379" --gcttl 54000` as an example to extend the retention period.
- Classification Note: This is classified as a self-managed BR operation topic because the content explains the checkpoint backup mechanism, retry behavior, command usage, and operational limitations involving PD, TiKV, `gc-safepoint`, and external storage.

## Official Source Content

# Checkpoint Backup

Snapshot backup might be interrupted due to recoverable errors, such as disk exhaustion and node crash. Before TiDB v6.5.0, data that is backed up before the interruption would be invalidated even after the error is addressed, and you need to start the backup from scratch. For large clusters, this incurs considerable extra cost.

In TiDB v6.5.0, Backup & Restore (BR) introduces the checkpoint backup feature to allow continuing an interrupted backup. This feature can retain most data of the interrupted backup.
## Application scenarios

If your TiDB cluster is large and cannot afford to back up again after a failure, you can use the checkpoint backup feature. The br command-line tool (hereinafter referred to as `br`) periodically records the shards that have been backed up. In this way, the next backup retry can use the backup progress close to the abnormal exit.
## Implementation details

During a snapshot backup, `br` encodes the tables into the corresponding key space, and generates backup RPC requests before sending them to TiKV nodes. After receiving the backup request, TiKV nodes back up the data within the requested range. Every time a TiKV node finishes backing up data of a Region, it returns the backup information of this range to `br`.

`br` records the information returned by TiKV nodes, which helps `br` get the key ranges that have been backed up. The checkpoint backup feature periodically uploads the new backup information to external storage so that the key ranges that have been backed up can be persisted.

When `br` retries the backup, it reads the key ranges that have been backed up from external storage, and compares them with the key ranges of the backup task. The differential data helps `br` to determine the key range that still needs to be backed up in checkpoint backup.
## Usage limitations

Checkpoint backup relies on the GC mechanism and cannot recover all data that has been backed up. The following sections provide the details.
### Backup retry must be prior to GC

During the backup, `br` periodically updates the `gc-safepoint` of the backup snapshot in PD to avoid data being garbage collected. When `br` exits, the `gc-safepoint` cannot be updated in time. As a result, before the next backup retry, the data might have been garbage collected.

To avoid this situation, `br` keeps the `gc-safepoint` for about one hour by default when `gcttl` is not specified. You can set the `gcttl` parameter to extend the retention period if needed .

The following example sets `gcttl` to 15 hours (54000 seconds) to extend the retention period of `gc-safepoint`:

```shell
tiup br backup full \
--storage local:///br_data/ --pd "${PD_IP}:2379" \
--gcttl 54000
```

> **Note:**
>
> The `gc-safepoint` created before backup is deleted after the snapshot backup is completed. You do not need to delete it manually.
### Some data needs to be backed up again

When `br` retries backup, some data that has been backed up might need to be backed up again, including the data being backed up and the data not recorded by the checkpoint.

- If the interruption is caused by an error, `br` will persist the meta information of the data backed up before exit. In this case, only the data being backed up needs to be backed up again in the next retry.

- If the `br` process is interrupted by the system, `br` cannot persist the meta information of the data backed up to the external storage. Since `br` persists the meta information every 30 seconds, data backed up in the last 30 seconds before interruption cannot be persisted and needs to be backed up again in the next retry.
