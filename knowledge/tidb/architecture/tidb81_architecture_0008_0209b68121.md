# BR backup and restore architecture overview

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/backup-and-restore-design.md`
- Source Title: `Overview of TiDB Backup & Restore Architecture`
- Source Heading Path: `Overview of TiDB Backup & Restore Architecture`
- Source Line Ranges: `5-23`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `operator`, `tikv`
- Topic Tags: `backup`, `restore`, `architecture`, `snapshot-backup`, `log-backup`, `pitr`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0008_0209b68121`
- Source ID: `tidb-docs-8.1:br/backup-and-restore-design.md#overview-of-tidb-backup-restore-architecture`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ac4ee7b8f1285df4b353ef1458cb7f301d05931f4469f5d6c7ae07bc2cc9d257`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/backup-and-restore-design#overview-of-tidb-backup-restore-architecture
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/backup-and-restore-design.md

## Retrieval Guidance

- Use When: Use this chunk when the request asks for an overview of TiDB Backup & Restore architecture or where BR and TiDB Operator fit in backup, restore, log backup, and PITR workflows.
- Retrieval Keywords: TiDB Backup & Restore Architecture, BR backup and restore architecture overview, BR, TiDB Operator, TiKV nodes, full data backup and restore, snapshot backup, restore snapshot backup data, data change log backup, log backup: backup of KV data change, point-in-time recovery, PITR
- Follow-up Guidance: The source points to the architecture documents for Back up snapshot data, Restore snapshot backup data, Log backup: backup of KV data change, and PITR.
- Classification Note: This is classified as architecture because the content gives a high-level overview of how BR and TiDB Operator access backup and restore features and links to the architecture of each feature.

## Official Source Content

# Overview of TiDB Backup & Restore Architecture

As described in [TiDB Backup & Restore Overview](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview), TiDB supports backing up and restoring multiple types of cluster data. You can use Backup & Restore (BR) and TiDB Operator to access these features, and create tasks to back up data from TiKV nodes or restore data to TiKV nodes.

For details about the architecture of each backup and restore feature, see the following documents:

- Full data backup and restore

    - [Back up snapshot data](https://docs.pingcap.com/tidb/stable/br/br-snapshot-architecture#process-of-backup)
    - [Restore snapshot backup data](https://docs.pingcap.com/tidb/stable/br/br-snapshot-architecture#process-of-restore)

- Data change log backup

    - [Log backup: backup of KV data change](https://docs.pingcap.com/tidb/stable/br/br-log-architecture#process-of-log-backup)

- Point-in-time recovery (PITR)

    - [PITR](https://docs.pingcap.com/tidb/stable/br/br-log-architecture#process-of-pitr)
