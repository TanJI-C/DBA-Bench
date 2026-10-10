# TiDB 4.0.0 Beta.2 release notes: compatibility, features, and fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.0-beta.2.md`
- Source Title: `TiDB 4.0.0 Beta.2 Release Notes`
- Source Heading Path: `TiDB 4.0.0 Beta.2 Release Notes | TiDB 4.0.0 Beta.2 Release Notes > Compatibility Changes | TiDB 4.0.0 Beta.2 Release Notes > New Features | TiDB 4.0.0 Beta.2 Release Notes > Bug Fixes`
- Source Line Ranges: `5-60`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `ticdc`, `br`, `lightning`, `tidb`, `tiflash`
- Topic Tags: `release-notes`, `compatibility`, `new-features`, `bug-fixes`, `dynamic-configuration`, `bidirectional-replication`, `tls`, `change-data-capture`, `incremental-backup`, `arm-deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0146_17882aa4fd`
- Source ID: `tidb-docs-8.1:releases/release-4.0.0-beta.2.md#tidb-4-0-0-beta-2-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bc8bad5e628c8dcc74f7f8034f92d1682ecd84ee811240a46c1f2dc2a0442906`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.0-beta.2#tidb-4-0-0-beta-2-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.0-beta.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.0-beta.2 release notes covering compatibility changes, new features, and bug fixes across TiDB, TiKV, PD, TiCDC, BR, TiDB Binlog, TiDB Lightning, TiFlash, and TiDB Ansible.
- Retrieval Keywords: TiDB 4.0.0 Beta.2 Release Notes, 4.0.0-beta.2, Compatibility Changes, New Features, Bug Fixes, dynamically updated configuration, persisting the dynamically updated configuration into the hardware disk, TiDB Binlog, disable-dispatch, disable-causality, Drainer, bidirectional data replication between TiDB clusters, TiDB Lightning, TLS configuration, TiCDC, change data capture, capturing changed data from TiKV, replicating the changed data to Kafka, eventual data consistency, row-level orderliness, process-level high availability, Backup & Restore, BR, incremental backup, Amazon S3, TiDB Ansible, injecting the node information to etcd, ARM platform, empty short values during the backup, Hibernate Regions, rule checker fails to allocate stores to Regions, replication delay when the Leader is being switched, BR version is not compatible with the TiDB version, BR version is not compatible with TiFlash
- Follow-up Guidance: The source further organizes the content into Compatibility Changes, New Features, and Bug Fixes with per-component items for TiKV, PD, Tools, and TiDB Ansible.
- Classification Note: This is a self-managed release-notes chunk summarizing version 4.0.0-beta.2 compatibility changes, feature additions, and fixes across multiple TiDB ecosystem components.

## Official Source Content

# TiDB 4.0.0 Beta.2 Release Notes

Release date: March 18, 2020

TiDB version: 4.0.0-beta.2

TiDB Ansible version: 4.0.0-beta.2
## Compatibility Changes

+ Tools
    - TiDB Binlog
        - Fix the issue that the system returns an error and exits when `disable-dispatch` and `disable-causality` are configured in Drainer [#915](https://github.com/pingcap/tidb-binlog/pull/915)
## New Features

+ TiKV
    - Support persisting the dynamically updated configuration into the hardware disk [#6684](https://github.com/tikv/tikv/pull/6684)

+ PD
    - Support persisting the dynamically updated configuration into the hardware disk [#2153](https://github.com/pingcap/pd/pull/2153)

+ Tools
    - TiDB Binlog
        - Support the bidirectional data replication between TiDB clusters [#879](https://github.com/pingcap/tidb-binlog/pull/879) [#903](https://github.com/pingcap/tidb-binlog/pull/903)
    - TiDB Lightning
        - Support the TLS configuration [#40](https://github.com/tikv/importer/pull/40) [#270](https://github.com/pingcap/tidb-lightning/pull/270)
    - TiCDC
        - Initial release of the change data capture (CDC), providing the following features:
            - Support capturing changed data from TiKV
            - Support replicating the changed data from TiKV to MySQL compatible databases, and guarantee the eventual data consistency
            - Support replicating the changed data to Kafka, and guarantee either the eventual data consistency or the row-level orderliness
            - Provide process-level high availability
    - Backup & Restore (BR)
        - Enable experimental features such as incremental backup and backing up files to Amazon S3 [#175](https://github.com/pingcap/br/pull/175)

+ TiDB Ansible
    - Support injecting the node information to etcd [#1196](https://github.com/pingcap/tidb-ansible/pull/1196)
    - Support deploying TiDB services on the ARM platform [#1204](https://github.com/pingcap/tidb-ansible/pull/1204)
## Bug Fixes

+ TiKV
    - Fix the panic issue that might occur when meeting empty short values during the backup [#6718](https://github.com/tikv/tikv/pull/6718)
    - Fix the issue that Hibernate Regions might not be correctly awakened in some cases [#6772](https://github.com/tikv/tikv/pull/6672) [#6648](https://github.com/tikv/tikv/pull/6648) [#6376](https://github.com/tikv/tikv/pull/6736)

+ PD
    - Fix the panic issue that the rule checker fails to allocate stores to Regions [#2160](https://github.com/pingcap/pd/pull/2160)
    - Fix the issue that after the dynamic configuration is enabled, the configuration might have replication delay when the Leader is being switched [#2154](https://github.com/pingcap/pd/pull/2154)

+ Tools
    - Backup & Restore (BR)
        - Fix the issue that BR might fail to restore data of a large size because PD cannot process large-sized data [#167](https://github.com/pingcap/br/pull/167)
        - Fix the BR failure occurred because the BR version is not compatible with the TiDB version [#186](https://github.com/pingcap/br/pull/186)
        - Fix the BR failure occurred because the BR version is not compatible with TiFlash [#194](https://github.com/pingcap/br/pull/194)
