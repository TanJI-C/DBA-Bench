# Log backup storage maintenance and metadata inspection

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-pitr-manual.md`
- Source Title: `TiDB Log Backup and PITR Command Manual`
- Source Heading Path: `TiDB Log Backup and PITR Command Manual > Perform log backup > Clean up backup data | TiDB Log Backup and PITR Command Manual > Perform log backup > View the backup metadata`
- Source Line Ranges: `258-340`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `shared`
- Topic Tags: `log-backup`, `storage-maintenance`, `truncate`, `metadata`, `external-storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0020_df01595122`
- Source ID: `tidb-docs-8.1:br/br-pitr-manual.md#clean-up-backup-data`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `592b7064ba033e14077146051b72b9f209c5dec103ed093b30588af13ad99c54`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-pitr-manual#clean-up-backup-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-pitr-manual.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how to clean outdated log backup data from backup storage or inspect log backup metadata such as the earliest and latest restorable timestamps.
- Retrieval Keywords: tiup br log truncate, tiup br log metadata, --dry-run, --until, --storage, truncate the incremental log until sometime, get the metadata of log backup storage, log-min-ts, log-max-ts, log-min-date, log-max-date, Clean up backup data, View the backup metadata, backup storage, Amazon S3, GCS, Azure Blob Storage
- Follow-up Guidance: The source shows that both commands only access the backup storage and do not access the TiDB cluster.
- Classification Note: This is classified as operation because the content describes BR commands for storage maintenance and metadata inspection of log backup data.

## Official Source Content

### Clean up backup data

You can run the `tiup br log truncate` command to clean up the outdated or no longer needed log backup data.

Run `tiup br log truncate --help` to see the help information:

```shell
tiup br log truncate --help
truncate the incremental log until sometime.

Usage:
  br log truncate [flags]

Flags:
  --dry-run        Run the command but don't really delete the files.
  -h, --help       help for truncate
  --until string   Remove all backup data until this TS.(support TSO or datetime, e.g. '400036290571534337' or '2018-05-11 01:42:23+0800'.)
  -y, --yes        Skip all prompts and always execute the command.


Global Flags:
  -s, --storage string         specify the url where backup storage, eg, "s3://bucket/path/prefix"
```

This command only accesses the backup storage and does not access the TiDB cluster. Some parameters are described as follows:

- `--dry-run`: run the command but do not really delete the files.
- `--until`: delete all log backup data before the specified timestamp.
- `--storage`: the backup storage address. Currently, BR supports Amazon S3, GCS, or Azure Blob Storage as the storage for log backup. For details, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).

Usage example:

```shell
tiup br log truncate --until='2022-07-26 21:20:00+0800' \
--storage='s3://backup-101/logbackup?access-key=${access-key}&secret-access-key=${secret-access-key}'
```

Expected output:

```shell
Reading Metadata... DONE; take = 277.911599ms
We are going to remove 9 files, until 2022-07-26 21:20:00.0000.
Sure? (y/N) y
Clearing data files... DONE; take = 43.504161ms, kv-count = 53, kv-size = 4573(4.573kB)
Removing metadata... DONE; take = 24.038962ms
```
### View the backup metadata

You can run the `tiup br log metadata` command to view the backup metadata in the storage system, such as the earliest and latest timestamp that can be restored.

Run `tiup br log metadata --help` to see the help information:

```shell
tiup br log metadata --help
get the metadata of log backup storage

Usage:
  br log metadata [flags]

Flags:
  -h, --help       help for metadata

Global Flags:
  -s, --storage string         specify the url where backup storage, eg, "s3://bucket/path/prefix"
```

This command only accesses the backup storage and does not access the TiDB cluster.

The `--storage` parameter is used to specify the backup storage address. Currently, BR supports Amazon S3, GCS, or Azure Blob Storage as the storage for log backup. For details, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).

Usage example:

```shell
tiup br log metadata --storage='s3://backup-101/logbackup?access-key=${access-key}&secret-access-key=${secret-access-key}'
```

Expected output:

```shell
[2022/07/25 23:02:57.236 +08:00] [INFO] [collector.go:69] ["log metadata"] [log-min-ts=434582449885806593] [log-min-date="2022-07-14 20:08:03.268 +0800"] [log-max-ts=434834300106964993] [log-max-date="2022-07-25 23:00:15.618 +0800"]
```
