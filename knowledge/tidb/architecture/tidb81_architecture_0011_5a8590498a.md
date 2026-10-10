# BR snapshot backup and restore architecture and workflow

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-snapshot-architecture.md`
- Source Title: `TiDB Snapshot Backup and Restore Architecture`
- Source Heading Path: `TiDB Snapshot Backup and Restore Architecture | TiDB Snapshot Backup and Restore Architecture > Architecture | TiDB Snapshot Backup and Restore Architecture > Process of backup | TiDB Snapshot Backup and Restore Architecture > Process of restore`
- Source Line Ranges: `5-89`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `snapshot-backup`, `snapshot-restore`, `workflow`, `scheduling`, `gc`, `region`, `metadata`, `sst`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0011_5a8590498a`
- Source ID: `tidb-docs-8.1:br/br-snapshot-architecture.md#tidb-snapshot-backup-and-restore-architecture`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `07453314d04fe8f4d59f28d40cda4c1b97cc9d17203ac02e44776c3d27054de3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-snapshot-architecture#tidb-snapshot-backup-and-restore-architecture
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-snapshot-architecture.md

## Retrieval Guidance

- Use When: Use this chunk when you need the end-to-end BR snapshot backup or restore workflow, including how BR coordinates with PD and TiKV and which retry conditions appear during restore.
- Retrieval Keywords: BR snapshot backup and restore architecture, br backup full, br restore, Pause GC, Fetch TiKV and Region info, Request TiKV to back up data, Generate SST, Upload SST, back up schemas, Upload metadata, Pause Region schedule, Split & scatter Region, rewrite rules, Rewrite KVs, Ingest SST, RegionNotFound, EpochNotMatch, backup timestamp, data checksum, file checksum
- Follow-up Guidance: It also details that backup metadata includes the backup timestamp, table and corresponding backup files, data checksum, and file checksum, and that restore rewrites table ID and index ID before ingesting SST into RocksDB.
- Classification Note: This is classified as architecture because the content explains the BR snapshot backup and restore process flow, component interactions among BR, PD, and TiKV, and the operational stages of scheduling, data movement, and retry handling.

## Official Source Content

# TiDB Snapshot Backup and Restore Architecture

This document introduces the architecture and process of TiDB snapshot backup and restore using a Backup & Restore (BR) tool as an example.
## Architecture

The TiDB snapshot backup and restore architecture is as follows:

![BR snapshot backup and restore architecture](/media/br/br-snapshot-arch.png)
## Process of backup

The process of a cluster snapshot backup is as follows:

![snapshot backup process design](/media/br/br-snapshot-backup-ts.png)

The complete backup process is as follows:

1. BR receives the `br backup full` command.

    * Gets the backup time point and storage path.

2. BR schedules the backup data.

    * **Pause GC**: BR configures the TiDB GC time to prevent the backup data from being cleaned up by [TiDB GC mechanism](https://docs.pingcap.com/tidb/stable/garbage-collection-overview).
    * **Fetch TiKV and Region info**: BR accesses PD to get all TiKV nodes addresses and [Region](https://docs.pingcap.com/tidb/stable/tidb-storage#region) distribution of data.
    * **Request TiKV to back up data**: BR creates a backup request and sends it to all TiKV nodes. The backup request includes the backup time point, Regions to be backed up, and the storage path.

3. TiKV accepts the backup request and initiates a backup worker.

4. TiKV backs up the data.

    * **Scan KVs**: the backup worker reads data corresponding to the backup time point from the Region where the leader locates.
    * **Generate SST**: the backup worker saves the data to SST files, which are stored in the memory.
    * **Upload SST**: the backup worker uploads the SST files to the storage path.

5. BR receives the backup result from each TiKV node.

    * If some data fails to be backed up due to Region changes, for example, a TiKV node is down, BR will retry the backup.
    * If there is any data fails to be backed up and cannot be retried, the backup task fails.
    * After all data is backed up, BR will then back up the metadata.

6. BR backs up the metadata.

    * **Back up schemas**: BR backs up the table schemas and calculates the checksum of the table data.
    * **Upload metadata**: BR generates the backup metadata and uploads it to the storage path. The backup metadata includes the backup timestamp, the table and corresponding backup files, data checksum, and file checksum.
## Process of restore

The process of a cluster snapshot restore is as follows:

![snapshot restore process design](/media/br/br-snapshot-restore-ts.png)

The complete restore process is as follows:

1. BR receives the `br restore` command.

    * Gets the data storage path and the database or table to be restored.
    * Checks whether the table to be restored exists and whether it meets the requirements for restore.

2. BR schedules the restore data.

    * **Pause Region schedule**: BR requests PD to pause the automatic Region scheduling during restore.
    * **Restore schema**: BR gets the schema of the backup data and the database and table to be restored. Note that the ID of a newly created table might be different from that of the backup data.
    * **Split & scatter Region**: BR requests PD to allocate Regions (split Region) based on backup data, and schedules Regions to be evenly distributed to storage nodes (scatter Region). Each Region has a specified data range `[start key, end key)`.
    * **Request TiKV to restore data**: BR creates a restore request and sends it to the corresponding TiKV nodes according to the result of Region split. The restore request includes the data to be restored and rewrite rules.

3. TiKV accepts the restore request and initiates a restore worker.

    * The restore worker calculates the backup data that needs to be read to restore.

4. TiKV restores the data.

    * **Download SST**: the restore worker downloads corresponding SST files from the storage path to a local directory.
    * **Rewrite KVs**: the restore worker rewrites the KV data according to the new table ID, that is, replace the original table ID in the [Key-Value](https://docs.pingcap.com/tidb/stable/tidb-computing#mapping-table-data-to-key-value) with the new table ID. The restore worker also rewrites the index ID in the same way.
    * **Ingest SST**: the restore worker ingests the processed SST files into RocksDB.
    * **Report restore result**: the restore worker reports the restore result to BR.

5. BR receives the restore result from each TiKV node.

    * If some data fails to be restored due to `RegionNotFound` or `EpochNotMatch`, for example, a TiKV node is down, BR will retry the restore.
    * If there is any data fails to be restored and cannot be retried, the restore task fails.
    * After all data is restored, the restore task succeeds.
