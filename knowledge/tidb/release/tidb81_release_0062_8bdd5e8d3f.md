# TiDB 2.1.14 release notes across TiDB, TiKV, PD, Binlog tools, and TiDB Ansible

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1.14.md`
- Source Title: `TiDB 2.1.14 Release Notes`
- Source Heading Path: `TiDB 2.1.14 Release Notes | TiDB 2.1.14 Release Notes > TiDB | TiDB 2.1.14 Release Notes > TiKV | TiDB 2.1.14 Release Notes > PD | TiDB 2.1.14 Release Notes > Tools | TiDB 2.1.14 Release Notes > TiDB Ansible`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `release-notes`, `bug-fixes`, `query-results`, `memory-usage`, `system-variables`, `auto-increment`, `processlist`, `binlog`, `pump`, `drainer`, `reparo`, `ansible`, `configuration`, `raftstore`, `logging`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0062_8bdd5e8d3f`
- Source ID: `tidb-docs-8.1:releases/release-2.1.14.md#tidb-2-1-14-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8de71c9cab589b5a8d0f0dcc9ce56da7990428c81f249deeed59cd81d70ad34a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1.14#tidb-2-1-14-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1.14.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 2.1.14 release-note fixes and additions across TiDB, TiKV, PD, TiDB Binlog tools, and TiDB Ansible, including query result fixes, processlist memory visibility, max execution time, auto-increment behavior, binlog space controls, and logging changes.
- Retrieval Keywords: TiDB 2.1.14 Release Notes, 2.1.14, show processlist, information_schema.processlist, MEM column, max_execution_time, MAX_EXECUTION_TIME, MemTracker, Distsql, OOMAction, Cancel, TRACE statement, mysql.expr_pushdown_blacklist, ONLY_FULL_GROUP_BY, ANY_VALUE, load data, auto-increment ID, column pruning, Raftstore message, empty callback, PD invalid configuration item, Warning, Reparo safe-mode, Pump stop-write-at-available-space, Garbage Collector, LevelDB L0 files, Drainer BIT columns, TiDB Ansible precheck, jmespath, jinja2
- Follow-up Guidance: The source groups the changes by TiDB, TiKV, PD, Tools, and TiDB Ansible and names the exact configuration items, system variables, tables, and statements changed in 2.1.14.
- Classification Note: This chunk is classified as a self-managed release-notes summary because it documents version 2.1.14 bug fixes and feature changes for multiple components, including TiDB, TiKV, PD, Binlog tools, and TiDB Ansible.

## Official Source Content

# TiDB 2.1.14 Release Notes

Release date: July 04, 2019

TiDB version: 2.1.14

TiDB Ansible version: 2.1.14
## TiDB

- Fix wrong query results caused by column pruning in some cases [#11019](https://github.com/pingcap/tidb/pull/11019)
- Fix the wrongly displayed information in `db` and `info` columns of `show processlist` [#11000](https://github.com/pingcap/tidb/pull/11000)
- Fix the issue that `MAX_EXECUTION_TIME` as a SQL hint and global variable does not work in some cases [#10999](https://github.com/pingcap/tidb/pull/10999)
- Support automatically adjust the incremental gap allocated by auto-increment ID based on the load [#10997](https://github.com/pingcap/tidb/pull/10997)
- Fix the issue that the `Distsql` memory information of `MemTracker` is not correctly cleaned when a query ends [#10971](https://github.com/pingcap/tidb/pull/10971)
- Add the `MEM` column in the `information_schema.processlist` table to describe the memory usage of a query [#10896](https://github.com/pingcap/tidb/pull/10896)
- Add the `max_execution_time` global system variable to control the maximum execution time of a query [#10940](https://github.com/pingcap/tidb/pull/10940)
- Fix the panic caused by using unsupported aggregate functions [#10911](https://github.com/pingcap/tidb/pull/10911)
- Add an automatic rollback feature for the last transaction when the `load data` statement fails [#10862](https://github.com/pingcap/tidb/pull/10862)
- Fix the issue that TiDB returns a wrong result in some cases when the `OOMAction` configuration item is set to `Cancel` [#11016](https://github.com/pingcap/tidb/pull/11016)
- Disable the `TRACE` statement to avoid the TiDB panic issue [#11039](https://github.com/pingcap/tidb/pull/11039)
- Add the `mysql.expr_pushdown_blacklist` system table that dynamically enables/disables pushing down specific functions to Coprocessor [#10998](https://github.com/pingcap/tidb/pull/10998)
- Fix the issue that the `ANY_VALUE` function does not work in the `ONLY_FULL_GROUP_BY` mode [#10994](https://github.com/pingcap/tidb/pull/10994)
- Fix the incorrect evaluation caused by not doing a deep copy when evaluating the user variable of the string type [#11043](https://github.com/pingcap/tidb/pull/11043)
## TiKV

- Optimize processing the empty callback when processing the Raftstore message to avoid sending unnecessary message [#4682](https://github.com/tikv/tikv/pull/4682)
## PD

- Adjust the log output level from `Error` to `Warning` when reading an invalid configuration item [#1577](https://github.com/pingcap/pd/pull/1577)
## Tools

TiDB Binlog

- Reparo
    - Add the `safe-mode` configuration item, and support importing duplicated data after this item is enabled [#662](https://github.com/pingcap/tidb-binlog/pull/662)
- Pump
    - Add the `stop-write-at-available-space` configuration item to limit the available binlog space [#659](https://github.com/pingcap/tidb-binlog/pull/659)
    - Fix the issue that Garbage Collector does not work sometimes when the number of LevelDB L0 files is 0 [#648](https://github.com/pingcap/tidb-binlog/pull/648)
    - Optimize the algorithm of deleting log files to speed up releasing the space [#648](https://github.com/pingcap/tidb-binlog/pull/648)
- Drainer
    - Fix the failure to update `BIT` columns in the downstream [#655](https://github.com/pingcap/tidb-binlog/pull/655)
## TiDB Ansible

- Add the precheck feature for the `ansible` command and its `jmespath` and `jinja2` dependency packages [#807](https://github.com/pingcap/tidb-ansible/pull/807)
- Add the `stop-write-at-available-space` parameter (10 GiB by default) in Pump, and stop writing binlog files in Pump when the available disk space is less than the parameter value [#807](https://github.com/pingcap/tidb-ansible/pull/807)
