# TiDB 3.0.3 release notes across TiDB, TiKV, PD, tools, and Ansible

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.3.md`
- Source Title: `TiDB 3.0.3 Release Notes`
- Source Heading Path: `TiDB 3.0.3 Release Notes | TiDB 3.0.3 Release Notes > TiDB | TiDB 3.0.3 Release Notes > TiKV | TiDB 3.0.3 Release Notes > PD | TiDB 3.0.3 Release Notes > Tools | TiDB 3.0.3 Release Notes > TiDB Ansible`
- Source Line Ranges: `5-79`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `lightning`, `ecosystem`
- Topic Tags: `release-notes`, `bug-fixes`, `sql-optimizer`, `sql-execution`, `server`, `ddl`, `monitoring`, `readindex`, `deadlock`, `pdctl`, `binlog`, `drainer`, `import`, `ansible`, `rolling-update`, `alerting`, `spark`, `tispark`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0118_ad97e15722`
- Source ID: `tidb-docs-8.1:releases/release-3.0.3.md#tidb-3-0-3-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1908cde649ee5dc77ac469acab95c5dd4e73b917ee8ffd74d5ecc933f129e9a5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.3#tidb-3-0-3-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.3.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 3.0.3 release-note changes, bug fixes, and compatibility updates across TiDB, TiKV, PD, Tools, and TiDB Ansible.
- Retrieval Keywords: TiDB 3.0.3 Release Notes, release date August 29 2019, TiDB version 3.0.3, TiDB Ansible version 3.0.3, opt_rule_blacklist, aggregation_eliminate, column_prune, Index Join prefix index unsigned index negative value, create binding parsing errors, Quote function null value, ifnull Max Min NotNullFlag, bit type data in string form, sequential read OOM, if coalesce unsigned parameters, Div unsigned decimal types, Pump Drainer status panic, select ... for update Autocommit = 1, set default role permission check, create user drop user permission check, PointGetExecutor auto retry, Window function partition boundary error, time function EOF errors, Explain inconsistent with executed plan, slow log Succ field, tidb_backoff_weight, minimum TiKV version compatible v3.0.0, tidb_ddl_reorg_worker_cnt, tidb_ddl_reorg_batch_size, backoff monitoring types, ReadIndex duplicate context, PutStore scheduling jitters, Region heartbeats timestamps, dead lock detector, grpc env deadlock clients, config-check, ReadIndex no leader, pdctl success message, defaultBinlogItemCount 512, Drainer startup OOM, pump server offline logic, TiDB Lightning skip system databases by default, mysql information_schema performance_schema sys, rolling update PD operations, Grafana Collector components, TiKV alerting rules, pessimistic-txn, Spark V2.4.3, TiSpark V2.1.4
- Follow-up Guidance: The content groups the changes by TiDB, TiKV, PD, Tools, and TiDB Ansible, including specific identifiers such as opt_rule_blacklist, tidb_backoff_weight, tidb_ddl_reorg_worker_cnt, tidb_ddl_reorg_batch_size, defaultBinlogItemCount, and pessimistic-txn.
- Classification Note: This chunk is classified as a self-managed release note because the official content is the TiDB 3.0.3 release notes covering component-specific fixes and updates, including TiDB Ansible items.

## Official Source Content

# TiDB 3.0.3 Release Notes

Release date: August 29, 2019

TiDB version: 3.0.3

TiDB Ansible version: 3.0.3
## TiDB

+ SQL Optimizer
    - Add the `opt_rule_blacklist` table to disable logic optimization rules such as `aggregation_eliminate` and `column_prune` [#11658](https://github.com/pingcap/tidb/pull/11658)
    - Fix the issue that incorrect results might be returned for `Index Join` when the join key uses a prefix index or an unsigned index column that is equal to a negative value [#11759](https://github.com/pingcap/tidb/pull/11759)
    - Fix the issue that `"` or `\` in the `SELECT` statements of `create … binding ...` might result in parsing errors [#11726](https://github.com/pingcap/tidb/pull/11726)
+ SQL Execution Engine
    - Fix the issue that type errors in the return value might occur when the Quote function handles a null value [#11619](https://github.com/pingcap/tidb/pull/11619)
    - Fix the issue that incorrect results for `ifnull` might be returned when Max/Min is used for type inferring with `NotNullFlag` retained [#11641](https://github.com/pingcap/tidb/pull/11641)
    - Fix the potential error that occurs when comparing bit type data in string form [#11660](https://github.com/pingcap/tidb/pull/11660)
    - Decrease the concurrency for data that requires sequential read to lower the possibility of OOM [#11679](https://github.com/pingcap/tidb/pull/11679)
    - Fix the issue that incorrect type inferring might be caused when multiple parameters are unsigned for some built-in functions (for example, `if` and `coalesce`) [#11621](https://github.com/pingcap/tidb/pull/11621)
    - Fix the incompatibility with MySQL when the `Div` function handles unsigned decimal types [#11813](https://github.com/pingcap/tidb/pull/11813)
    - Fix the issue that panic might occur when executing SQL statements that modify the status of Pump/Drainer [#11827](https://github.com/pingcap/tidb/pull/11827)
    - Fix the issue that panic might occur for `select ... for update` when Autocommit = 1 and there is no `begin` statement [#11736](https://github.com/pingcap/tidb/pull/11736)
    - Fix the permission check error that might occur when the `set default role` statement is executed [#11777](https://github.com/pingcap/tidb/pull/11777)
    - Fix the permission check error that might occur when `create user` or `drop user` is executed [#11814](https://github.com/pingcap/tidb/pull/11814)
    - Fix the issue that the `select ... for update` statement might auto retry when it is constructed into the `PointGetExecutor` function [#11718](https://github.com/pingcap/tidb/pull/11718)
    - Fix the boundary error that might occur when the Window function handles partition [#11825](https://github.com/pingcap/tidb/pull/11825)
    - Fix the issue that the `time` function hits EOF errors when handling an incorrectly formatted argument [#11893](https://github.com/pingcap/tidb/pull/11893)
    - Fix the issue that the Window function does not check the passed-in parameters [#11705](https://github.com/pingcap/tidb/pull/11705)
    - Fix the issue that the plan result viewed via `Explain` is inconsistent with the actually executed plan [#11186](https://github.com/pingcap/tidb/pull/11186)
    - Fix the issue that duplicate memory referenced by the Window function might result in a crash or incorrect results [#11823](https://github.com/pingcap/tidb/pull/11823)
    - Update the incorrect information in the `Succ` field in the slow log [#11887](https://github.com/pingcap/tidb/pull/11887)
+ Server
    - Rename the `tidb_back_off_wexight` variable to `tidb_backoff_weight` [#11665](https://github.com/pingcap/tidb/pull/11665)
    - Update the minimum TiKV version compatible with the current TiDB to v3.0.0 [#11618](https://github.com/pingcap/tidb/pull/11618)
    - Support `make testSuite` to ensure the suites in the test are correctly used [#11685](https://github.com/pingcap/tidb/pull/11685)
+ DDL
    - Skip the execution of unsupported partition-related DDL statements, including statements that modify the partition type while deleting multiple partitions [#11373](https://github.com/pingcap/tidb/pull/11373)
    - Disallow a Generated Column to be placed before its dependent columns [#11686](https://github.com/pingcap/tidb/pull/11686)
    - Modify the default values of `tidb_ddl_reorg_worker_cnt` and `tidb_ddl_reorg_batch_size` [#11874](https://github.com/pingcap/tidb/pull/11874)
+ Monitor
    - Add new backoff monitoring types to record duration for each backoff type; add more backoff metrics to cover previously uncounted types such as commit backoff [#11728](https://github.com/pingcap/tidb/pull/11728)
## TiKV

- Fix the issue that ReadIndex might fail to respond to requests because of duplicate context [#5256](https://github.com/tikv/tikv/pull/5256)
- Fix potential scheduling jitters caused by premature `PutStore` [#5277](https://github.com/tikv/tikv/pull/5277)
- Fix incorrect timestamps reported from Region heartbeats [#5296](https://github.com/tikv/tikv/pull/5296)
- Reduce the size of core dump by excluding the shared block cache from it [#5322](https://github.com/tikv/tikv/pull/5322)
- Fix potential TiKV panics during region merge [#5291](https://github.com/tikv/tikv/pull/5291)
- Speed up leader change check for the dead lock detector [#5317](https://github.com/tikv/tikv/pull/5317)
- Support using `grpc env` to create deadlock clients [#5346](https://github.com/tikv/tikv/pull/5346)
- Add `config-check` to check whether the configuration is correct [#5349](https://github.com/tikv/tikv/pull/5349)
- Fix the issue that ReadIndex does not return anything when there is no leader [#5351](https://github.com/tikv/tikv/pull/5351)
## PD

- Return success message for `pdctl` [#1685](https://github.com/pingcap/pd/pull/1685)
## Tools

+ TiDB Binlog
    - Modify the default value of `defaultBinlogItemCount` in Drainer from 65536 to 512 to reduce the chance of OOM on Drainer startup [#721](https://github.com/pingcap/tidb-binlog/pull/721)
    - Optimize the offline logic for pump server to avoid potential offline congestions [#701](https://github.com/pingcap/tidb-binlog/pull/701)
+ TiDB Lightning:
    - Skip the system databases `mysql`, `information_schema`, `performance_schema`, and `sys` by default when importing [#225](https://github.com/pingcap/tidb-lightning/pull/225)
## TiDB Ansible

- Optimize PD operations for rolling update to improve stability [#894](https://github.com/pingcap/tidb-ansible/pull/894)
- Remove the Grafana Collector components that are not supported by the current Grafana version [#892](https://github.com/pingcap/tidb-ansible/pull/892)
- Update TiKV alerting rules [#898](https://github.com/pingcap/tidb-ansible/pull/898)
- Fix the issue that the generated TiKV configuration misses the `pessimistic-txn` parameter [#911](https://github.com/pingcap/tidb-ansible/pull/911)
- Update Spark to V2.4.3, and update TiSpark to V2.1.4 that is compatible with Spark V2.4.3 [#913](https://github.com/pingcap/tidb-ansible/pull/913), [#918](https://github.com/pingcap/tidb-ansible/pull/918)
