# PITR restore point command and restore constraints

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-pitr-manual.md`
- Source Title: `TiDB Log Backup and PITR Command Manual`
- Source Heading Path: `TiDB Log Backup and PITR Command Manual > Restore to a specified point in time (PITR)`
- Source Line Ranges: `341-402`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `tikv`
- Topic Tags: `pitr`, `restore`, `point-in-time-recovery`, `full-backup`, `log-restore`, `tls`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0008_bbdb248d7d`
- Source ID: `tidb-docs-8.1:br/br-pitr-manual.md#restore-to-a-specified-point-in-time-pitr`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5aa240b46207e8c51f59b145c3dc1c7297d4bb809ad28979322b729e157b252d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-pitr-manual#restore-to-a-specified-point-in-time-pitr
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-pitr-manual.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the `tiup br restore point` command, its PITR parameters, and the documented constraints for restoring full backup and log backup data to a specified point in time.
- Retrieval Keywords: tiup br restore point, restore data from log until specify commit timestamp, --full-backup-storage, --restored-ts, --start-ts, --pitr-batch-count, --pitr-batch-size, --pitr-concurrency, --pd, --ca, --cert, --key, --storage, PITR, point-in-time recovery, restore only log backup data, new cluster, checkpoint of the backup data
- Follow-up Guidance: The source notes that the first restore must specify the full snapshot data, repeated restore of the same log backup time range might be inconsistent, and multiple log restore batches must be restored in consecutive order to keep data consistent.
- Classification Note: This is classified as recovery because the content explains BR point-in-time restore behavior, restore parameters, and restore consistency constraints.

## Official Source Content

## Restore to a specified point in time (PITR)

You can run the `tiup br restore point` command to perform a PITR on a new cluster or just restore the log backup data.

Run `tiup br restore point --help` to see the help information:

```shell
tiup br restore point --help
restore data from log until specify commit timestamp

Usage:
  br restore point [flags]

Flags:
  --full-backup-storage string specify the backup full storage. fill it if want restore full backup before restore log.
  -h, --help                   help for point
  --pitr-batch-count uint32    specify the batch count to restore log. (default 8)
  --pitr-batch-size uint32     specify the batch size to restore log. (default 16777216)
  --pitr-concurrency uint32    specify the concurrency to restore log. (default 16)
  --restored-ts string         the point of restore, used for log restore. support TSO or datetime, e.g. '400036290571534337' or '2018-05-11 01:42:23+0800'
  --start-ts string            the start timestamp which log restore from. support TSO or datetime, e.g. '400036290571534337' or '2018-05-11 01:42:23+0800'


Global Flags:
 --ca string                  CA certificate path for TLS connection
 --cert string                Certificate path for TLS connection
 --key string                 Private key path for TLS connection
 -u, --pd strings             PD address (default [127.0.0.1:2379])
 -s, --storage string         specify the url where backup storage, eg, "s3://bucket/path/prefix"
```

The example output only shows the common parameters. These parameters are described as follows:

- `--full-backup-storage`: the storage address for the snapshot (full) backup. To use PITR, specify this parameter and choose the latest snapshot backup before the restore timestamp. To restore only log backup data, you can omit this parameter. Note that when initializing the recovery cluster for the first time, you must specify a snapshot backup. Currently, BR supports Amazon S3, GCS, and Azure Blob Storage as the storage for log backup. For details, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).
- `--pitr-batch-count`: the maximum number of files in a single batch when restoring log data. Once this threshold is reached, the current batch ends immediately and the next batch starts.
- `--pitr-batch-size`: the maximum data size (in bytes) in a single batch when restoring log data. Once this threshold is reached, the current batch ends immediately and the next batch starts.
- `--pitr-concurrency`: the number of concurrent tasks during log restore. Each concurrent task restores one batch of log data at a time.
- `--restored-ts`: the timestamp that you want to restore data to. If this parameter is not specified, BR restores data to the latest timestamp available in the log backup, that is, the checkpoint of the backup data.
- `--start-ts`: the start timestamp that you want to restore log backup data from. If you only need to restore log backup data, you must specify this parameter.
- `--pd`: the PD address of the restore cluster.
- `--ca`, `--cert`, `--key`: specify the mTLS encryption method to communicate with TiKV and PD.
- `--storage`: the storage address for the log backup. Currently, BR supports Amazon S3, GCS, or Azure Blob Storage as the storage for log backup. For details, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).

Usage example:

```shell
tiup br restore point --pd="${PD_IP}:2379"
--storage='s3://backup-101/logbackup?access-key=${access-key}&secret-access-key=${secret-access-key}'
--full-backup-storage='s3://backup-101/snapshot-202205120000?access-key=${access-key}&secret-access-key=${secret-access-key}'

Full Restore <--------------------------------------------------------------------------------------------------------------------------------------------------------> 100.00%
*** ***["Full Restore success summary"] ****** [total-take=3.112928252s] [restore-data-size(after-compressed)=5.056kB] [Size=5056] [BackupTS=434693927394607136] [total-kv=4] [total-kv-size=290B] [average-speed=93.16B/s]
Restore Meta Files <--------------------------------------------------------------------------------------------------------------------------------------------------> 100.00%
Restore KV Files <----------------------------------------------------------------------------------------------------------------------------------------------------> 100.00%
"restore log success summary"] [total-take=192.955533ms] [restore-from=434693681289625602] [restore-to=434693753549881345] [total-kv-count=33] [total-size=21551]
```

> **Note:**
>
> - When you restore the cluster for the first time, you must specify the full snapshot data. Otherwise, some data in the newly created table might be incorrect due to rewriting Table ID rules.
> - You cannot restore the log backup data of a certain time period repeatedly. If you restore the log backup data of a range `[t1=10, t2=20)` repeatedly, the restored data might be inconsistent.
> - When you restore log data of different time periods in multiple batches, ensure that the log data is restored in consecutive order. If you restore the log backup data of `[t1, t2)`, `[t2, t3)`, and `[t3, t4)` in consecutive order, the restored data is consistent. However, if you restore `[t1, t2)` and then skip `[t2, t3)` to restore `[t3, t4)`, the restored data might be inconsistent.
