# Backup and restore methods and throughput FAQs

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/manage-cluster-faq.md`
- Source Title: `TiDB Cluster Management FAQs`
- Source Heading Path: `TiDB Cluster Management FAQs > Backup and restoration | TiDB Cluster Management FAQs > Backup and restoration > How to back up data in TiDB? | TiDB Cluster Management FAQs > Backup and restoration > How is the speed of backup and restore?`
- Source Line Ranges: `446-458`
- Source Scope: `all`
- Primary Component: `br`
- Related Components: `dumpling`, `shared`
- Topic Tags: `backup`, `restore`, `tool-selection`, `throughput`, `large-datasets`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0148_ea712c5a2c`
- Source ID: `tidb-docs-8.1:faq/manage-cluster-faq.md#backup-and-restoration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4b51090f9e5529335dec8dab1f03212683935b23bfcf8a1bc94a781a66476f8c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/manage-cluster-faq#backup-and-restoration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/manage-cluster-faq.md

## Retrieval Guidance

- Use When: Use this chunk when selecting a TiDB backup tool for large datasets or when looking up the documented backup and restore throughput of BR per TiKV instance.
- Retrieval Keywords: Backup & Restore (BR), Dumpling, mysqldump, large volume of data more than 1 TB, How to back up data in TiDB, How is the speed of backup and restore, 40 MB/s per TiKV instance, 100 MB/s per TiKV instance, backup and restoration, BR FAQs
- Follow-up Guidance: For more FAQs about BR, see BR FAQs.
- Classification Note: The official content is an operation FAQ for the BR-related backup and restoration topic, including tool selection guidance and stated throughput figures.

## Official Source Content

## Backup and restoration

This section describes common problems you may encounter during backup and restoration, their causes, and solutions.
### How to back up data in TiDB?

Currently, for the backup of a large volume of data (more than 1 TB), the preferred method is using [Backup & Restore (BR)](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview). Otherwise, the recommended tool is [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview). Although the official MySQL tool `mysqldump` is also supported in TiDB to back up and restore data, its performance is no better than BR and it needs much more time to back up and restore large volumes of data.

For more FAQs about BR, see [BR FAQs](https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq).
### How is the speed of backup and restore?

When [BR](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview) is used to perform backup and restore tasks, the backup is processed at about 40 MB/s per TiKV instance, and restore is processed at about 100 MB/s per TiKV instance.
