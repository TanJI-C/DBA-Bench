# Run incremental backup with last backup timestamp

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-incremental-guide.md`
- Source Title: `TiDB Incremental Backup and Restore Guide`
- Source Heading Path: `TiDB Incremental Backup and Restore Guide > Back up incremental data`
- Source Line Ranges: `20-40`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `tikv`, `tiup`
- Topic Tags: `incremental-backup`, `lastbackupts`, `validate`, `storage`, `ratelimit`, `s3`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0017_cbb564d229`
- Source ID: `tidb-docs-8.1:br/br-incremental-guide.md#back-up-incremental-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1de5e64ce23c82e5135c3b101a7045fed76cf7626626287f979e495f129dd681`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-incremental-guide#back-up-incremental-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-incremental-guide.md

## Retrieval Guidance

- Use When: Use this chunk when answering how to run an incremental backup with BR by obtaining the previous backup end timestamp and passing --lastbackupts.
- Retrieval Keywords: Back up incremental data, tiup br backup full, --lastbackupts, LAST_BACKUP_TS, tiup br validate decode, --field="end-version", validate decode end-version, current PD timestamp, --ratelimit, maximum speed per TiKV, storage path of backup data, save the incremental backup data under a different path, s3://backup-101/snapshot-202209081330/incr
- Follow-up Guidance: The source shows using tiup br validate decode --field="end-version" to get LAST_BACKUP_TS and storing incremental data in a different path such as the incr directory.
- Classification Note: This is operation content because it provides the BR commands, flags, and storage-path requirement for creating an incremental backup.

## Official Source Content

## Back up incremental data

To back up incremental data, run the `tiup br backup` command with **the last backup timestamp** `--lastbackupts` specified. In this way, br command-line tool automatically backs up incremental data generated between `lastbackupts` and the current time. To get `--lastbackupts`, run the `validate` command. The following is an example:

```shell
LAST_BACKUP_TS=`tiup br validate decode --field="end-version" --storage "s3://backup-101/snapshot-202209081330?access-key=${access-key}&secret-access-key=${secret-access-key}"| tail -n1`
```

The following command backs up the incremental data between `(LAST_BACKUP_TS, current PD timestamp]` and the DDLs generated during this time period:

```shell
tiup br backup full --pd "${PD_IP}:2379" \
--storage "s3://backup-101/snapshot-202209081330/incr?access-key=${access-key}&secret-access-key=${secret-access-key}" \
--lastbackupts ${LAST_BACKUP_TS} \
--ratelimit 128
```

- `--lastbackupts`: The last backup timestamp.
- `--ratelimit`: The maximum speed **per TiKV** performing backup tasks (in MiB/s).
- `storage`: The storage path of backup data. You need to save the incremental backup data under a different path from the previous snapshot backup. In the preceding example, incremental backup data is saved in the `incr` directory under the full backup data. For details, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).
