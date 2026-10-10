# PD TiKV tools and TiDB Ansible release changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.9.md`
- Source Title: `TiDB 2.1.9 Release Notes`
- Source Heading Path: `TiDB 2.1.9 Release Notes > PD | TiDB 2.1.9 Release Notes > TiKV | TiDB 2.1.9 Release Notes > Tools | TiDB 2.1.9 Release Notes > TiDB Ansible`
- Source Line Ranges: `43-69`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tikv`, `lightning`
- Topic Tags: `release-notes`, `pd-operator`, `leader-transfer`, `binlog`, `lightning`, `importer`, `sst-upload`, `compression`, `checkpoint`, `ansible`, `slow-query-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0082_e25d763e9b`
- Source ID: `tidb-docs-8.1:releases/release-2.1.9.md#pd`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d11682d59f72da85945d9d419d932be271d53dccb55aa56aaad165dcf22c6b35`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.9#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.9.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 2.1.9 release changes in PD, TiKV, TiDB Binlog, TiDB Lightning, sync-diff-inspector, or TiDB Ansible.
- Retrieval Keywords: TiDB 2.1.9 Release Notes, PD GetOperator service, TiKV transferring leader quorum changes, TiDB Binlog unsigned int type primary key column minus numbers, downstream is pb, downstream name from pb to file, Reparo wrong UPDATE statements, TiDB Lightning bit type incorrectly parsed, Fill the lacking column data in dump files using row id or the default column value, Importer SST files fail to be imported but it still returns successful import result, speed limit in Importer when uploading SST files to TiKV, Importer RocksDB SST compression method lz4, sync-diff-inspector checkpoint, enable_slow_query_log, inventory.ini, slow query log to a separate log file by default
- Follow-up Guidance: The source also notes that TiDB Ansible removes the enable_slow_query_log parameter from inventory.ini and outputs the slow query log to a separate log file by default.
- Classification Note: This is a shared release-notes chunk because it summarizes 2.1.9 updates across multiple components including PD, TiKV, Tools, and TiDB Ansible.

## Official Source Content

## PD

- Support the GetOperator service [#1514](https://github.com/pingcap/pd/pull/1514)
## TiKV

- Fix potential quorum changes when transferring leader [#4604](https://github.com/tikv/tikv/pull/4604)
## Tools

- TiDB Binlog
    - Fix the issue that data replication is interrupted because data in the unsigned int type of primary key column are minus numbers [#574](https://github.com/pingcap/tidb-binlog/pull/574)
    - Remove the compression option when the downstream is `pb` and change the downstream name from `pb` to `file` [#597](https://github.com/pingcap/tidb-binlog/pull/575)
    - Fix the bug that Reparo introduced in 2.1.7 generates wrong `UPDATE` statements [#576](https://github.com/pingcap/tidb-binlog/pull/576)
- TiDB Lightning
    - Fix the bug that the bit type of column data is incorrectly parsed by the parser [#164](https://github.com/pingcap/tidb-lightning/pull/164)
    - Fill the lacking column data in dump files using row id or the default column value [#174](https://github.com/pingcap/tidb-lightning/pull/174)
    - Fix the Importer bug that some SST files fail to be imported but it still returns successful import result [#4566](https://github.com/tikv/tikv/pull/4566)
    - Support setting a speed limit in Importer when uploading SST files to TiKV [#4607](https://github.com/tikv/tikv/pull/4607)
    - Change Importer RocksDB SST compression method to `lz4` to reduce CPU consumption [#4624](https://github.com/tikv/tikv/pull/4624)
- sync-diff-inspector
    - Support checkpoint [#227](https://github.com/pingcap/tidb-tools/pull/227)
## TiDB Ansible

- Update links in tidb-ansible documentation according to docs refactoring [#740](https://github.com/pingcap/tidb-ansible/pull/740), [#741](https://github.com/pingcap/tidb-ansible/pull/741)
- Remove the `enable_slow_query_log` parameter in the `inventory.ini` file and output the slow query log to a separate log file by default [#742](https://github.com/pingcap/tidb-ansible/pull/742)
