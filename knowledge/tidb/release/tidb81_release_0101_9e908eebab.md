# TiKV, PD, Tools, and TiDB Ansible release changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.10.md`
- Source Title: `TiDB 3.0.10 Release Notes`
- Source Heading Path: `TiDB 3.0.10 Release Notes > TiKV | TiDB 3.0.10 Release Notes > PD | TiDB 3.0.10 Release Notes > Tools | TiDB 3.0.10 Release Notes > TiDB Ansible`
- Source Line Ranges: `50-74`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `ticdc`, `lightning`, `dashboard`
- Topic Tags: `release-notes`, `raftstore`, `region-merge`, `data-loss`, `leader-scheduling`, `region-cache`, `tso`, `relay-log`, `configuration-defaults`, `web-interface`, `monitoring`, `pd-leader`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0101_9e908eebab`
- Source ID: `tidb-docs-8.1:releases/release-3.0.10.md#tikv`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `42ffa52a68055cb8ead096fc931f29f18a8885fb21555cbbb9183ee8bd547e9a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.10#tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.10.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 3.0.10 release-note changes outside the TiDB server, including TiKV raftstore fixes, PD cache and TSO updates, TiDB Binlog and Lightning tool changes, and TiDB Ansible monitoring or PD leader related fixes.
- Retrieval Keywords: TiKV 3.0.10 release notes, Raftstore Region merge failure panic data loss, yield scheduling fairness pre-transferring the leader, PD automatically updating the Region cache information, leader lease time determine TSO service validity, TiDB Binlog Drainer relay log, TiDB Lightning configuration items default values when a config file is missing, TiDB Lightning web interface cannot be opened in the non-server mode, TiDB Ansible failure to obtain PD leader, Deadlock Detect Duration monitoring item in the TiDB dashboard, Statement Lock Keys Count monitoring item in the TiDB dashboard, Statement Pessimistic Retry Count monitoring item in the TiDB dashboard
- Follow-up Guidance: The source groups these changes by component under TiKV, PD, Tools, and TiDB Ansible in the TiDB 3.0.10 release notes.
- Classification Note: This is classified as a shared release-notes chunk because it summarizes component-specific changes across TiKV, PD, Tools, and TiDB Ansible rather than a single primary server component.

## Official Source Content

## TiKV

+ Raftstore
    - Fix the system panic issue #6460 or data loss issue #598 caused by Region merge failure [#6481](https://github.com/tikv/tikv/pull/6481)
    - Support `yield` to optimize scheduling fairness, and support pre-transferring the leader to improve leader scheduling stability [#6563](https://github.com/tikv/tikv/pull/6563)
## PD

- Fix the invalid cache issue by supporting automatically updating the Region cache information when the system traffic changes [#2103](https://github.com/pingcap/pd/pull/2103)
- Use leader lease time to determine TSO service validity [#2117](https://github.com/pingcap/pd/pull/2117)
## Tools

+ TiDB Binlog
    - Support relay log in Drainer [#893](https://github.com/pingcap/tidb-binlog/pull/893)
+ TiDB Lightning
    - Make some configuration items use default values when a config file is missing [#255](https://github.com/pingcap/tidb-lightning/pull/255)
    - Fix the issue that the web interface cannot be opened in the non-server mode [#259](https://github.com/pingcap/tidb-lightning/pull/259)
## TiDB Ansible

- Fix the issue that the command execution fails due to the failure to obtain PD leader in some scenarios [#1121](https://github.com/pingcap/tidb-ansible/pull/1121)
- Add the `Deadlock Detect Duration` monitoring item in the TiDB dashboard [#1127](https://github.com/pingcap/tidb-ansible/pull/1127)
- Add the `Statement Lock Keys Count` monitoring item in the TiDB dashboard [#1132](https://github.com/pingcap/tidb-ansible/pull/1132)
- Add the `Statement Pessimistic Retry Count` monitoring item in the TiDB dashboard [#1133](https://github.com/pingcap/tidb-ansible/pull/1133)
