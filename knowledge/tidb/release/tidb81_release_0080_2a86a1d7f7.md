# TiDB 2.1.8 release notes across TiDB, PD, TiKV, Tools, and TiDB Ansible

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.8.md`
- Source Title: `TiDB 2.1.8 Release Notes`
- Source Heading Path: `TiDB 2.1.8 Release Notes | TiDB 2.1.8 Release Notes > TiDB | TiDB 2.1.8 Release Notes > PD | TiDB 2.1.8 Release Notes > TiKV | TiDB 2.1.8 Release Notes > Tools | TiDB 2.1.8 Release Notes > TiDB Ansible`
- Source Line Ranges: `5-64`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `lightning`, `ticdc`
- Topic Tags: `release-notes`, `bug-fixes`, `compatibility`, `statistics`, `optimizer`, `logging`, `metrics`, `performance`, `binlog`, `replication`, `configuration`, `ansible`, `upgrade-limits`, `os-support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0080_2a86a1d7f7`
- Source ID: `tidb-docs-8.1:releases/release-2.1.8.md#tidb-2-1-8-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `040eb3376902ea49811448d18401ac91412df5125ff072a0c3c8149f49ffc231`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.8#tidb-2-1-8-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.8.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the official TiDB 2.1.8 release notes for bug fixes, new configuration items, metrics, compatibility changes, or upgrade and OS support limits across TiDB, PD, TiKV, Tools, and TiDB Ansible.
- Retrieval Keywords: TiDB 2.1.8 Release Notes, TiDB version 2.1.8, TiDB Ansible version 2.1.8, GROUP_CONCAT NULL-valued parameter, Distinct mode decimal equality check, SHOW FULL COLUMNS date datetime timestamp collation, row count estimation correlated columns, DATE_ADD DATE_SUB compatibility, STR_TO_DATE %H format, Optimizer Hints unmatched table name warning, Unified Log Format, NULL values inaccurate statistics estimation, time_zone validation, 2019.01.01 time format, EXPLAIN row count estimation displayed incorrectly, KILL TIDB [session id], predicate pushdown constant filtering conditions, read-only statement not processed correctly, regionScatterer invalid OperatorStep, hot store incorrect statistics of keys, MergeRegion operator timeout, PD server handling TSO requests elapsed time metrics, wrong statistics of the read traffic, raftstore performance issue when too many Regions exist, level_zero_slowdown_writes_trigger/2, Lightning Checksum Analyze import order, Lightning encoding SQL performance, storage.sync-log, TiDB Binlog Pump, traffic compression between Pump and Drainer, syncer.sql-mode, syncer.ignore-table, CentOS 7.0 or later, Red Hat 7.0 or later, epollexclusive, rolling update prohibit upgrading 2.0.1 or earlier to 2.1 or later
- Follow-up Guidance: The source also lists exact component-specific fixes and additions under the TiDB, PD, TiKV, Tools, and TiDB Ansible sections of the TiDB 2.1.8 release notes.
- Classification Note: This chunk is classified as a self-managed release note because it announces the April 12, 2019 TiDB 2.1.8 release and enumerates official changes for multiple components, including deployment-related TiDB Ansible limits.

## Official Source Content

# TiDB 2.1.8 Release Notes

Release date: April 12, 2019

TiDB version: 2.1.8

TiDB Ansible version: 2.1.8
## TiDB

- Fix the issue that the processing logic of `GROUP_CONCAT` function is incompatible with MySQL when there is a NULL-valued parameter [#9930](https://github.com/pingcap/tidb/pull/9930)
- Fix the equality check issue of decimal values in the `Distinct` mode [#9931](https://github.com/pingcap/tidb/pull/9931)
- Fix the collation compatibility issue of the date, datetime, and timestamp types for the `SHOW FULL COLUMNS` statement
    - [#9938](https://github.com/pingcap/tidb/pull/9938)
    - [#10114](https://github.com/pingcap/tidb/pull/10114)
- Fix the issue that the row count estimation is inaccurate when the filtering condition contains correlated columns [#9937](https://github.com/pingcap/tidb/pull/9937)
- Fix the compatibility issue between the `DATE_ADD` and `DATE_SUB` functions
    - [#9963](https://github.com/pingcap/tidb/pull/9963)
    - [#9966](https://github.com/pingcap/tidb/pull/9966)
- Support the `%H` format for the `STR_TO_DATE` function to improve compatibility [#9964](https://github.com/pingcap/tidb/pull/9964)
- Fix the issue that the result is wrong when the `GROUP_CONCAT` function groups by a unique index [#9969](https://github.com/pingcap/tidb/pull/9969)
- Return a warning when the Optimizer Hints contains an unmatched table name [#9970](https://github.com/pingcap/tidb/pull/9970)
- Unify the log format to facilitate collecting logs using tools for analysis Unified Log Format
- Fix the issue that a lot of NULL values cause inaccurate statistics estimation [#9979](https://github.com/pingcap/tidb/pull/9979)
- Fix the issue that an error is reported when the default value of the TIMESTAMP type is the boundary value [#9987](https://github.com/pingcap/tidb/pull/9987)
- Validate the value of `time_zone` [#10000](https://github.com/pingcap/tidb/pull/10000)
- Support the `2019.01.01` time format [#10001](https://github.com/pingcap/tidb/pull/10001)
- Fix the issue that the row count estimation is displayed incorrectly in the result returned by the `EXPLAIN` statement in some cases [#10044](https://github.com/pingcap/tidb/pull/10044)
- Fix the issue that `KILL TIDB [session id]` cannot instantly stop the execution of a statement in some cases [#9976](https://github.com/pingcap/tidb/pull/9976)
- Fix the predicate pushdown issue of constant filtering conditions in some cases [#10049](https://github.com/pingcap/tidb/pull/10049)
- Fix the issue that a read-only statement is not processed correctly in some cases [#10048](https://github.com/pingcap/tidb/pull/10048)
## PD

- Fix the issue that `regionScatterer` might generate an invalid `OperatorStep` [#1482](https://github.com/pingcap/pd/pull/1482)
- Fix the issue that a hot store makes incorrect statistics of keys [#1487](https://github.com/pingcap/pd/pull/1487)
- Fix the too short timeout issue of the `MergeRegion` operator [#1495](https://github.com/pingcap/pd/pull/1495)
- Add elapsed time metrics of the PD server handling TSO requests [#1502](https://github.com/pingcap/pd/pull/1502)
## TiKV

- Fix the issue of wrong statistics of the read traffic [#4441](https://github.com/tikv/tikv/pull/4441)
- Fix the raftstore performance issue when too many Regions exist [#4484](https://github.com/tikv/tikv/pull/4484)
- Do not ingest files when the number of level 0 SST files exceeds `level_zero_slowdown_writes_trigger/2` [#4464](https://github.com/tikv/tikv/pull/4464)
## Tools

- Optimize the order of importing tables for Lightning to reduce the effects of large tables executing `Checksum` and `Analyze` on the cluster during the importing process and improve the success rate of `Checksum` and `Analyze` [#156](https://github.com/pingcap/tidb-lightning/pull/156)
- Improve the encoding SQL performance by 50% for Lightning by directly parsing the data source file content to `types.Datum` of TiDB to avoid additional parsing working of the KV encoder [#145](https://github.com/pingcap/tidb-lightning/pull/145)
- Add the `storage.sync-log` configuration item in TiDB Binlog Pump to support flushing disks of the local storage asynchronously in Pump [#529](https://github.com/pingcap/tidb-binlog/pull/529)
- Support traffic compression of communication between TiDB Binlog Pump and Drainer [#530](https://github.com/pingcap/tidb-binlog/pull/530)
- Add the `syncer.sql-mode` configuration item in TiDB Binlog Drainer to support using different `sql-mode`s to parse DDL queries [#513](https://github.com/pingcap/tidb-binlog/pull/513)
- Add the `syncer.ignore-table` configuration item in TiDB Binlog Drainer to support filtering tables not to be replicated [#526](https://github.com/pingcap/tidb-binlog/pull/526)
## TiDB Ansible

- Modify the version limit for the operating system and only support CentOS 7.0 or later and Red Hat 7.0 or later [#734](https://github.com/pingcap/tidb-ansible/pull/734)
- Add the feature of checking whether `epollexclusive` is supported in every OS [#728](https://github.com/pingcap/tidb-ansible/pull/728)
- Add the version limit for rolling update to prohibit upgrading a version of 2.0.1 or earlier to a version of 2.1 or later [#728](https://github.com/pingcap/tidb-ansible/pull/728)
