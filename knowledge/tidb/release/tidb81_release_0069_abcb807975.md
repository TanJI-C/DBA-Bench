# TiDB 2.1.19 release notes for TiKV, PD, tools, and TiDB Ansible

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.19.md`
- Source Title: `TiDB 2.1.19 Release Notes`
- Source Heading Path: `TiDB 2.1.19 Release Notes > TiKV | TiDB 2.1.19 Release Notes > PD | TiDB 2.1.19 Release Notes > Tools | TiDB 2.1.19 Release Notes > TiDB Ansible`
- Source Line Ranges: `68-93`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `ecosystem`
- Topic Tags: `release-notes`, `raftstore`, `importer`, `etcd-upgrade`, `http-api`, `tidb-binlog`, `pump`, `drainer`, `monitoring`, `ansible`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0069_abcb807975`
- Source ID: `tidb-docs-8.1:releases/release-2.1.19.md#tikv`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7a1ba89c32f0c3b08bec1594c80ae9519615255aa94bd59d62c22efb84141573`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.19#tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.19.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 2.1.19 release-note changes in TiKV, PD, TiDB Binlog tools, or TiDB Ansible, especially Raftstore, Importer, HTTP API performance, etcd upgrade notes, Pump, Drainer, and monitoring updates.
- Retrieval Keywords: TiDB 2.1.19 Release Notes, TiKV, PD, Tools, TiDB Ansible, Raftstore, is_merging, Compact log, Importer, gRPC message length, HTTP API, getting all Regions, etcd PreVote cannot elect a leader, downgrade not supported, TiDB Binlog, binlogctl, Drainer filter configuration, Graceful exit of Pump, Pump writes binlog data, monitoring metrics, refresh table information after Drainer has executed a DDL operation, commit binlog of a DDL operation is ignored, Uncommon Error OPM, Write Binlog Error, TiSpark 2.1.8
- Follow-up Guidance: This chunk also includes the note that PD upgrades etcd to fix the PreVote leader election issue and that downgrade is not supported.
- Classification Note: The official content is classified as a multi-component release-notes chunk because it summarizes TiKV, PD, tools, and TiDB Ansible changes in TiDB 2.1.19.

## Official Source Content

## TiKV

+ Raftstore
    - Fix the panic occurred when restarting TiKV and `is_merging` is given an incorrect value in the process of merging Regions and applying the Compact log [#5884](https://github.com/tikv/tikv/pull/5884)
+ Importer
    - Remove the limit on the gRPC message length [#5809](https://github.com/tikv/tikv/pull/5809)
## PD

- Improve the performance of the HTTP API for getting all Regions [#1988](https://github.com/pingcap/pd/pull/1988)
- Upgrade etcd to fix the issue that etcd PreVote cannot elect a leader (downgrade not supported) [#2052](https://github.com/pingcap/pd/pull/2052)
## Tools

+ TiDB Binlog
    - Optimize the node status information output through binlogctl [#777](https://github.com/pingcap/tidb-binlog/pull/777)
    - Fix the panic occurred because of the `nil` value in the Drainer filter configuration [#802](https://github.com/pingcap/tidb-binlog/pull/802)
    - Optimize the `Graceful` exit of Pump [#825](https://github.com/pingcap/tidb-binlog/pull/825)
    - Add more detailed monitoring metrics when Pump writes binlog data [#830](https://github.com/pingcap/tidb-binlog/pull/830)
    - Optimize Drainer's logic to refresh table information after Drainer has executed a DDL operation [#836](https://github.com/pingcap/tidb-binlog/pull/836)
    - Fix the issue that the commit binlog of a DDL operation is ignored when Pump does not receive this binlog [#855](https://github.com/pingcap/tidb-binlog/pull/855)
## TiDB Ansible

- Rename the `Uncommon Error OPM` monitoring item of TiDB service to `Write Binlog Error` and add the corresponding alert message [#1038](https://github.com/pingcap/tidb-ansible/pull/1038)
- Upgrade TiSpark to 2.1.8 [#1063](https://github.com/pingcap/tidb-ansible/pull/1063)
