# TiDB 3.1 Beta.1 release notes for TiKV, BR, and TiDB Ansible

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.1.0-beta.1.md`
- Source Title: `TiDB 3.1 Beta.1 Release Notes`
- Source Heading Path: `TiDB 3.1 Beta.1 Release Notes | TiDB 3.1 Beta.1 Release Notes > TiKV | TiDB 3.1 Beta.1 Release Notes > Tools | TiDB 3.1 Beta.1 Release Notes > TiDB Ansible`
- Source Line Ranges: `5-40`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `br`, `pd`, `tiup`, `lightning`
- Topic Tags: `release-notes`, `backup`, `incremental-backup`, `restore`, `sst-import`, `monitoring`, `follower-read`, `region-splitting`, `partitioned-tables`, `pd-schedulers`, `thp`, `grafana`, `deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0133_70313e16ab`
- Source ID: `tidb-docs-8.1:releases/release-3.1.0-beta.1.md#tidb-3-1-beta-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8075741d06248baa20c99229f0b2c069067eee454ecfa0a45c834bd679047bb2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.1.0-beta.1#tidb-3-1-beta-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.1.0-beta.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 3.1.0-beta.1 release-note items covering TiKV backup and sst_importer changes, BR backup and restore updates, or TiDB Ansible deployment and monitoring additions.
- Retrieval Keywords: TiDB 3.1.0-beta.1, TiDB 3.1 Beta.1 Release Notes, TiKV backup incremental backup, start_key hash value backup file name, force_consistency_checks false positives, sst_importer MVCC properties restoring, tikv_import_download_duration, tikv_import_download_bytes, tikv_import_ingest_duration, tikv_import_ingest_bytes, tikv_import_error_counter, Follower Read stale data leader changes, BR inaccurate backup progress, splitting Regions performance, partitioned tables backup and restore, automatically scheduling PD schedulers, non PKIsHandle tables restored overwritten, TiDB Ansible Transparent Huge Pages THP, Grafana monitoring for BR components, TiDB Lightning automatically creating related directories
- Follow-up Guidance: The source also groups these updates under the TiKV, Tools > BR, and TiDB Ansible sections of the TiDB 3.1 Beta.1 release notes.
- Classification Note: This is a self-managed release-notes chunk summarizing changes across shared components including TiKV, BR, and TiDB Ansible in TiDB version 3.1.0-beta.1.

## Official Source Content

# TiDB 3.1 Beta.1 Release Notes

Release date: January 10, 2020

TiDB version: 3.1.0-beta.1

TiDB Ansible version: 3.1.0-beta.1
## TiKV

+ backup
    - Change the name of the backup file from `start_key` to the hash value of `start_key` to reduce the file name's length for easy reading [#6198](https://github.com/tikv/tikv/pull/6198)
    - Disable RocksDB's `force_consistency_checks` check to avoid false positives in the consistency check [#6249](https://github.com/tikv/tikv/pull/6249)
    - Add the incremental backup feature [#6286](https://github.com/tikv/tikv/pull/6286)

+ sst_importer
    - Fix the issue that the SST file does not have MVCC properties during restoring [#6378](https://github.com/tikv/tikv/pull/6378)
    - Add the monitoring items such as `tikv_import_download_duration`, `tikv_import_download_bytes`, `tikv_import_ingest_duration`, `tikv_import_ingest_bytes`, and `tikv_import_error_counter` to observe the overheads of downloading and ingesting SST files [#6404](https://github.com/tikv/tikv/pull/6404)
+ raftstore
    - Fix the issue of Follower Read that the follower reads stale data when the leader changes, thus breaking transaction isolation [#6343](https://github.com/tikv/tikv/pull/6343)
## Tools

+ BR (Backup and Restore)
    - Fix the inaccurate backup progress information [#127](https://github.com/pingcap/br/pull/127)
    - Improve the performance of splitting Regions [#122](https://github.com/pingcap/br/pull/122)
    - Add the backup and restore feature for partitioned tables [#137](https://github.com/pingcap/br/pull/137)
    - Add the feature of automatically scheduling PD schedulers [#123](https://github.com/pingcap/br/pull/123)
    - Fix the issue that data is overwritten after non `PKIsHandle` tables are restored [#139](https://github.com/pingcap/br/pull/139)
## TiDB Ansible

- Add the feature of automatically disabling Transparent Huge Pages (THP) in the operating system during the initialization phase [#1086](https://github.com/pingcap/tidb-ansible/pull/1086)
- Add the Grafana monitoring for BR components [#1093](https://github.com/pingcap/tidb-ansible/pull/1093)
- Optimize the deployment of TiDB Lightning by automatically creating related directories [#1104](https://github.com/pingcap/tidb-ansible/pull/1104)
