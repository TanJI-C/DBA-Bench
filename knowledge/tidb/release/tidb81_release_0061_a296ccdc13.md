# TiDB 2.1.13 release notes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.13.md`
- Source Title: `TiDB 2.1.13 Release Notes`
- Source Heading Path: `TiDB 2.1.13 Release Notes | TiDB 2.1.13 Release Notes > TiDB | TiDB 2.1.13 Release Notes > TiKV | TiDB 2.1.13 Release Notes > Tools`
- Source Line Ranges: `5-37`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `ecosystem`
- Topic Tags: `release-notes`, `tidb-features`, `tikv-fixes`, `binlog-tools`, `configuration`, `hotspot-mitigation`, `ddl`, `statistics`, `region-split`, `mysql-compatibility`, `oom-fix`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0061_a296ccdc13`
- Source ID: `tidb-docs-8.1:releases/release-2.1.13.md#tidb-2-1-13-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b0c51f81ad129907a39e77249a6f1667bab35186bab2e10776a58a87fa6df88c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.13#tidb-2-1-13-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.13.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 2.1.13 release notes covering new hotspot mitigation syntax and configuration, DDL and OOM fixes, TiKV fixes, or TiDB Binlog changes.
- Retrieval Keywords: TiDB 2.1.13 Release Notes, SHARD_ROW_ID_BITS, AUTO_INCREMENT, hotspot issue, update-stats, PRE_SPLIT_REGIONS, SPLIT TABLE table_name INDEX index_name, SPLIT TABLE BETWEEN REGIONS, KILL syntax panic, ADD_DATE compatibility, index join selectivity, execdetails.ExecDetails, OOM issue, invalid DDL metadata, TiKV block-size, incomplete snapshots, TiDB Binlog, Pump wrong offset, Drainer advertise-addr
- Follow-up Guidance: The source also lists TiKV fixes for incomplete snapshots and `block-size` validity, plus TiDB Binlog changes for Pump wrong offset handling and Drainer `advertise-addr`.
- Classification Note: This is a self-managed release-notes chunk for TiDB 2.1.13 that summarizes changes across TiDB, TiKV, and Tools rather than a task procedure or standalone reference page.

## Official Source Content

# TiDB 2.1.13 Release Notes

Release date: June 21, 2019

TiDB version: 2.1.13

TiDB Ansible version: 2.1.13
## TiDB

- Add a feature to use `SHARD_ROW_ID_BITS` to scatter row IDs when the column contains an `AUTO_INCREMENT` attribute to relieve the hotspot issue [#10788](https://github.com/pingcap/tidb/pull/10788)
- Optimize the lifetime of invalid DDL metadata to speed up recovering the normal execution of DDL operations after upgrading the TiDB cluster [#10789](https://github.com/pingcap/tidb/pull/10789)
- Fix the OOM issue in high concurrent scenarios caused by the failure to quickly release Coprocessor resources, resulted from the `execdetails.ExecDetails` pointer [#10833](https://github.com/pingcap/tidb/pull/10833)
- Add the `update-stats` configuration item to control whether to update statistics [#10772](https://github.com/pingcap/tidb/pull/10772)
- Add the following TiDB-specific syntax to support Region presplit to solve the hotspot issue:
- Add the `PRE_SPLIT_REGIONS` table option [#10863](https://github.com/pingcap/tidb/pull/10863)
- Add the `SPLIT TABLE table_name INDEX index_name` syntax [#10865](https://github.com/pingcap/tidb/pull/10865)
- Add the `SPLIT TABLE [table_name] BETWEEN (min_value...) AND (max_value...) REGIONS [region_num]` syntax [#10882](https://github.com/pingcap/tidb/pull/10882)
- Fix the panic issue caused by the `KILL` syntax in some cases [#10879](https://github.com/pingcap/tidb/pull/10879)
- Improve the compatibility with MySQL for `ADD_DATE` in some cases [#10718](https://github.com/pingcap/tidb/pull/10718)
- Fix the wrong estimation for the selectivity rate of the inner table selection in index join [#10856](https://github.com/pingcap/tidb/pull/10856)
## TiKV

- Fix the issue that incomplete snapshots are generated in the system caused by the iterator not checking the status [#4940](https://github.com/tikv/tikv/pull/4940)
- Add a feature to check the validity for the `block-size` configuration [#4930](https://github.com/tikv/tikv/pull/4930)
## Tools

- TiDB Binlog
    - Fix the wrong offset issue caused by Pump not checking the returned value when it fails to write data [#640](https://github.com/pingcap/tidb-binlog/pull/640)
    - Add the `advertise-addr` configuration in Drainer to support the bridge mode in the container environment [#634](https://github.com/pingcap/tidb-binlog/pull/634)
