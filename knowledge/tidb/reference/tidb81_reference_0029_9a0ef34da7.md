# Log backup file types and directory structure

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-log-architecture.md`
- Source Title: `TiDB Log Backup and PITR Architecture`
- Source Heading Path: `TiDB Log Backup and PITR Architecture > Log backup files | TiDB Log Backup and PITR Architecture > Log backup files > Structure of backup files`
- Source Line Ranges: `96-158`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`
- Topic Tags: `log-backup`, `files`, `metadata`, `global-checkpoint`, `directory-structure`, `truncate`, `storage-layout`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0029_9a0ef34da7`
- Source ID: `tidb-docs-8.1:br/br-log-architecture.md#log-backup-files`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4ae1257a81e86a37705a1a3064a884ccbcdf2e003ae3c0fcdf1f3b06af4d632c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-log-architecture#log-backup-files
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-log-architecture.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about log backup file names, metadata files, global checkpoint files, storage layout, or the directory structure used by log backup.
- Retrieval Keywords: Log backup files, Structure of backup files, {resolved_ts}-{uuid}.meta, {store_id}.ts, {min_ts}-{uuid}.log, v1_stream_truncate_safepoint.txt, backupmeta, global_checkpoint, v1, br log truncate, resolved_ts, global checkpoint ts, date hour store_id directory
- Follow-up Guidance: It states that when cleaning up storage, always use `br log truncate` instead of manually deleting data because metadata references the data files and manual deletion might lead to restore failures or data inconsistencies after restore.
- Classification Note: The classification is reference because the content primarily documents file types, filename meanings, and the on-storage directory structure for log backup data.

## Official Source Content

## Log backup files

Log backup generates the following types of files:

- `{resolved_ts}-{uuid}.meta` file: is generated every time each TiKV node uploads the log backup data and stores metadata of all log backup data files uploaded this time. The `{resolved_ts}` is the resolved timestamp of the TiKV node. The latest `resolved_ts` of the log backup task is the minimum resolved timestamp among all TiKV nodes. The `{uuid}` is generated randomly when the file is created.
- `{store_id}.ts` file: is updated with global checkpoint ts every time each TiKV node uploads the log backup data. The `{store_id}` is the store ID of the TiKV node.
- `{min_ts}-{uuid}.log` file: stores the KV change log data of the backup task. The `{min_ts}` is the minimum TSO timestamp of the KV change log data in the file, and the `{uuid}` is generated randomly when the file is created.
- `v1_stream_truncate_safepoint.txt` file: stores the timestamp corresponding to the latest backup data in storage that deleted by `br log truncate`.
### Structure of backup files

```
.
├── v1
│   ├── backupmeta
│   │   ├── ...
│   │   └── {resolved_ts}-{uuid}.meta
│   ├── global_checkpoint
│   │   └── {store_id}.ts
│   └── {date}
│       └── {hour}
│           └── {store_id}
│               ├── ...
│               └── {min_ts}-{uuid}.log
└── v1_stream_truncate_safepoint.txt
```

Explanation of the backup file directory structure:

- `backupmeta`: stores backup metadata. The `resolved_ts` in the filename indicates the backup progress, meaning that data before this TSO has been fully backed up. However, note that this TSO only reflects the progress of certain shards.
- `global_checkpoint`: represents the global backup progress. It records the latest point in time to which data can be restored using `br restore point`.
- `{date}/{hour}`: stores backup data for the corresponding date and hour. When cleaning up storage, always use `br log truncate` instead of manually deleting data. This is because the metadata references the data in this directory, and manual deletion might lead to restore failures or data inconsistencies after restore.

The following is an example:

```
.
├── v1
│   ├── backupmeta
│   │   ├── ...
│   │   ├── 435213818858112001-e2569bda-a75a-4411-88de-f469b49d6256.meta
│   │   ├── 435214043785779202-1780f291-3b8a-455e-a31d-8a1302c43ead.meta
│   │   └── 435214443785779202-224f1408-fff5-445f-8e41-ca4fcfbd2a67.meta
│   ├── global_checkpoint
│   │   ├── 1.ts
│   │   ├── 2.ts
│   │   └── 3.ts
│   └── 20220811
│       └── 03
│           ├── 1
│           │   ├── ...
│           │   ├── 435213866703257604-60fcbdb6-8f55-4098-b3e7-2ce604dafe54.log
│           │   └── 435214023989657606-72ce65ff-1fa8-4705-9fd9-cb4a1e803a56.log
│           ├── 2
│           │   ├── ...
│           │   ├── 435214102632857605-11deba64-beff-4414-bc9c-7a161b6fb22c.log
│           │   └── 435214417205657604-e6980303-cbaa-4629-a863-1e745d7b8aed.log
│           └── 3
│               ├── ...
│               ├── 435214495848857605-7bf65e92-8c43-427e-b81e-f0050bd40be0.log
│               └── 435214574492057604-80d3b15e-3d9f-4b0c-b133-87ed3f6b2697.log
└── v1_stream_truncate_safepoint.txt
```
