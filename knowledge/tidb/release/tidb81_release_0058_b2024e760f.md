# TiDB 2.1.11 release notes across TiDB, PD, TiKV, Tools, and TiDB Ansible

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.11.md`
- Source Title: `TiDB 2.1.11 Release Notes`
- Source Heading Path: `TiDB 2.1.11 Release Notes | TiDB 2.1.11 Release Notes > TiDB | TiDB 2.1.11 Release Notes > PD | TiDB 2.1.11 Release Notes > TiKV | TiDB 2.1.11 Release Notes > Tools | TiDB 2.1.11 Release Notes > TiDB Ansible`
- Source Line Ranges: `5-47`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `ticdc`
- Topic Tags: `release-notes`, `bug-fixes`, `sql`, `statistics`, `scheduling`, `hot-region`, `locks`, `snapshots`, `binlog`, `drainer`, `ansible`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0058_b2024e760f`
- Source ID: `tidb-docs-8.1:releases/release-2.1.11.md#tidb-2-1-11-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3938c9e9a64dc14292392569b4424131ca0b0773dd47d303c1ebf6f71f577ea0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.11#tidb-2-1-11-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.11.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 2.1.11 release notes and the bug fixes or configuration additions across TiDB, PD, TiKV, Tools, and TiDB Ansible.
- Retrieval Keywords: TiDB 2.1.11 Release Notes, TiDB version 2.1.11, TiDB Ansible version 2.1.11, delete from join incorrect schema, CONVERT() incorrect field type, unix_timestamp()-unix_timestamp(now()), period_diff MySQL 8.0, Virtual Column collecting statistics, SHOW OPEN TABLES, goroutine leak, tidb_snapshot time format parsing, hots Region balance-region, hot-region-schedule-limit, hot-region-cache-hits-threshold, learner reads an empty index, ScanLock, ResolveLock, received snapshots, TiDB Binlog WritePause, Drainer parameters
- Follow-up Guidance: The source groups the changes by TiDB, PD, TiKV, Tools, and TiDB Ansible and names the related statements, variables, and configuration items fixed or added in 2.1.11.
- Classification Note: This is a self-managed release-notes chunk because it summarizes component-specific fixes and configuration changes in the TiDB 2.1.11 release.

## Official Source Content

# TiDB 2.1.11 Release Notes

Release date: June 03, 2019

TiDB version: 2.1.11

TiDB Ansible version: 2.1.11
## TiDB

- Fix the issue that incorrect schema is used for `delete from join` [#10595](https://github.com/pingcap/tidb/pull/10595)
- Fix the issue that the built-in `CONVERT()` may return incorrect field type [#10263](https://github.com/pingcap/tidb/pull/10263)
- Merge non-overlapped feedback when updating bucket count [#10569](https://github.com/pingcap/tidb/pull/10569)
- Fix calculation errors of `unix_timestamp()-unix_timestamp(now())` [#10491](https://github.com/pingcap/tidb/pull/10491)
- Fix the incompatibility issue of `period_diff` with MySQL 8.0 [#10501](https://github.com/pingcap/tidb/pull/10501)
- Skip `Virtual Column` when collecting statistics to avoid exceptions [#10628](https://github.com/pingcap/tidb/pull/10628)
- Support the `SHOW OPEN TABLES` statement [#10374](https://github.com/pingcap/tidb/pull/10374)
- Fix the issue that goroutine leak may happen in some cases [#10656](https://github.com/pingcap/tidb/pull/10656)
- Fix the issue that setting the `tidb_snapshot` variable in some cases may cause incorrect parsing of time format  [#10637](https://github.com/pingcap/tidb/pull/10637)
## PD

- Fix the issue that hots Region may fail to be scheduled due to `balance-region` [#1551](https://github.com/pingcap/pd/pull/1551)
- Set hotspot related scheduling priorities to high [#1551](https://github.com/pingcap/pd/pull/1551)
- Add two configuration items [#1551](https://github.com/pingcap/pd/pull/1551)
    - `hot-region-schedule-limit` to control the maximum number of concurrent hotspot scheduling tasks
    - `hot-region-cache-hits-threshold` to identify a hot Region
## TiKV

- Fix the issue that the learner reads an empty index when there is only one leader and one learner [#4751](https://github.com/tikv/tikv/pull/4751)
- Process `ScanLock` and `ResolveLock` in the thread pool with a high priority to reduce their impacts on commands with a normal priority [#4791](https://github.com/tikv/tikv/pull/4791)
- Sync all files of received snapshots [#4811](https://github.com/tikv/tikv/pull/4811)
## Tools

- TiDB Binlog
    - Limit data deletion speed during GC to avoid QPS degrading caused by `WritePause` [#620](https://github.com/pingcap/tidb-binlog/pull/620)
## TiDB Ansible

- Add Drainer parameters [#760](https://github.com/pingcap/tidb-ansible/pull/760)
