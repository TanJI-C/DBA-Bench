# TiDB 3.0.12 release notes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.12.md`
- Source Title: `TiDB 3.0.12 Release Notes`
- Source Heading Path: `TiDB 3.0.12 Release Notes | TiDB 3.0.12 Release Notes > Compatibility Changes | TiDB 3.0.12 Release Notes > New Features | TiDB 3.0.12 Release Notes > Bug Fixes`
- Source Line Ranges: `5-52`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `release-notes`, `compatibility-changes`, `new-features`, `bug-fixes`, `binlog`, `certificates`, `ddl`, `flow-control`, `locking`, `region-heartbeats`, `ansible`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0103_f39bb68f12`
- Source ID: `tidb-docs-8.1:releases/release-3.0.12.md#tidb-3-0-12-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5428fca3202948e947230e72e4ff1f17bfece8be130d2c7fddea95892aed90dd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.12#tidb-3-0-12-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.12.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 3.0.12 release-note details about compatibility changes, new features, or bug fixes across TiDB, TiKV, PD, TiDB Binlog, and TiDB Ansible.
- Retrieval Keywords: TiDB 3.0.12 Release Notes, 3.0.12, Binlog_prewrite_time, Wait_prewrite_binlog_time, alter instance, cluster-verify-cn, DDL requests flow limiting, binlog write fails, kafka-client-id, Drainer, GRANT REVOKE atomicity, pessimistic lock partition table, max-index-length, FROM_UNIXTIME, consistency check parameter, Raftstore flow control, Region heartbeats, multiple Grafana Prometheus Alertmanager
- Follow-up Guidance: The source also states that some known issues exist in this version and recommends using the latest 3.0.x version.
- Classification Note: This is a self-managed release-notes chunk that summarizes compatibility changes, new features, and bug fixes for TiDB 3.0.12 and related components.

## Official Source Content

# TiDB 3.0.12 Release Notes

Release date: March 16, 2020

TiDB version: 3.0.12

TiDB Ansible version: 3.0.12

> **Warning:**
>
> Some known issues are found in this version, and these issues are fixed in new versions. It is recommended that you use the latest 3.0.x version.
## Compatibility Changes

+ TiDB
    - Fix the issue of inaccurate timing of prewrite binlog in slow query log. The original timing field was called `Binlog_prewrite_time`. After this fix, the name is changed to `Wait_prewrite_binlog_time`. [#15276](https://github.com/pingcap/tidb/pull/15276)
## New Features

+ TiDB
    - Support dynamic loading of the replaced certificate file by using the `alter instance` statement [#15080](https://github.com/pingcap/tidb/pull/15080) [#15292](https://github.com/pingcap/tidb/pull/15292)
    - Add the `cluster-verify-cn` configuration item. After configuration, the status service can only be used when with the corresponding CN certificate. [#15164](https://github.com/pingcap/tidb/pull/15164)
    - Add a flow limiting feature for DDL requests in each TiDB server to reduce the error reporting frequency of DDL request conflicts [#15148](https://github.com/pingcap/tidb/pull/15148)
    - Support exiting of the TiDB server when binlog write fails [#15339](https://github.com/pingcap/tidb/pull/15339)

+ Tools
    - TiDB Binlog
        - Add the `kafka-client-id` configuration item in Drainer, which supports connecting to Kafka clients to configure the client ID [#929](https://github.com/pingcap/tidb-binlog/pull/929)
## Bug Fixes

+ TiDB
    - Make `GRANT`, `REVOKE` guarantee atomicity when modifying multiple users [#15092](https://github.com/pingcap/tidb/pull/15092)
    - Fix the issue that the locking of pessimistic lock on the partition table failed to lock the correct row [#15114](https://github.com/pingcap/tidb/pull/15114)
    - Make the error message display according to the value of `max-index-length` in the configuration when the index length exceeds the limit [#15130](https://github.com/pingcap/tidb/pull/15130)
    - Fix the incorrect decimal point issue of the `FROM_UNIXTIME` function [#15270](https://github.com/pingcap/tidb/pull/15270)
    - Fix the issue of conflict detection failure or data index inconsistency caused by deleting records written by oneself in a transaction [#15176](https://github.com/pingcap/tidb/pull/15176)

+ TiKV
    - Fix the issue of conflict detection failure or data index inconsistency caused by inserting an existing key into a transaction and then deleting it immediately when disabling the consistency check parameter [#7054](https://github.com/tikv/tikv/pull/7054)
    - Introduce a flow control mechanism in Raftstore to solve the problem that without flow control, it might lead to too slow tracking and cause the cluster to be stuck, and the transaction size might cause frequent reconnection of TiKV connections [#7072](https://github.com/tikv/tikv/pull/7072) [#6993](https://github.com/tikv/tikv/pull/6993)

+ PD
    - Fix the issue of incorrect Region information caused by data race when PD processes Region heartbeats [#2233](https://github.com/pingcap/pd/pull/2233)

+ TiDB Ansible
    - Support deploying multiple Grafana/Prometheus/Alertmanager in a cluster [#1198](https://github.com/pingcap/tidb-ansible/pull/1198)
