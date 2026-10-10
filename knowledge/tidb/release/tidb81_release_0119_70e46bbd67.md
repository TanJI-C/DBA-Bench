# TiDB 3.0.4 release overview and highlights

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.4.md`
- Source Title: `TiDB 3.0.4 Release Notes`
- Source Heading Path: `TiDB 3.0.4 Release Notes`
- Source Line Ranges: `5-41`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiup`
- Topic Tags: `release-notes`, `new-features`, `improvements`, `changed-behaviors`, `fixed-issues`, `slow-query-log`, `region-split`, `pessimistic-locking`, `recovery-speed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0119_70e46bbd67`
- Source ID: `tidb-docs-8.1:releases/release-3.0.4.md#tidb-3-0-4-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `85cc10af307737b801b575e54289a12dbaf2434f02578b5e3585504bcf93b483`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.4#tidb-3-0-4-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for a high-level summary of TiDB 3.0.4 release highlights, changed behaviors, and fixed issues across TiDB, TiKV, PD, TiDB Ansible, and Reparo.
- Retrieval Keywords: TiDB 3.0.4 Release Notes, performance_schema.events_statements_summary_by_digest, SHOW TABLE REGIONS WHERE, worker-count, txn-batch, batch Region split command, empty split command, iosnoop, funcslower, txn-local-latches.enable, tidb_txn_mode, Index_names, split-region-max-num, Out Of Memory Quota, tidb_allow_remove_auto_inc, PRE_SPLIT_REGIONS, adjacent small Regions cannot be merged, file descriptor leak in idle clusters
- Follow-up Guidance: For component-specific details, see the TiDB, TiKV, and PD sections in the same release notes.
- Classification Note: This is a release overview chunk because it summarizes new features, improvements, changed behaviors, fixed issues, and release metadata for TiDB 3.0.4.

## Official Source Content

# TiDB 3.0.4 Release Notes

Release date: October 8, 2019

TiDB version: 3.0.4

TiDB Ansible version: 3.0.4

- New features
    - Add the `performance_schema.events_statements_summary_by_digest` system table to troubleshoot performance issues at the SQL level
    - Add the `WHERE` clause in TiDB's `SHOW TABLE REGIONS` syntax
    - Add the `worker-count` and `txn-batch` configuration items in Reparo to control the recovery speed
- Improvements
    - Support batch Region split command and empty split command in TiKV to improve split performance
    - Support double linked list for RocksDB in TiKV to improve performance of reverse scan
    - Add two perf tools `iosnoop` and `funcslower` in TiDB Ansible to better diagnose the cluster state
    - Optimize the output of slow query logs in TiDB by deleting redundant fields
- Changed behaviors
    - Update the default value of `txn-local-latches.enable` to `false` to disable the default behavior of checking conflicts of local transactions in TiDB
    - Add the `tidb_txn_mode` system variable of global scope in TiDB and allow using the pessimistic lock; note that TiDB still adopts the optimistic lock by default
    - Replace the `Index_ids` field in TiDB slow query logs with `Index_names` to improve the usability of slow query logs
    - Add the `split-region-max-num` parameter in the TiDB configuration file to modify the maximum number of Regions allowed in the `SPLIT TABLE` syntax
    - Return the `Out Of Memory Quota` error instead of disconnecting the link when a SQL execution exceeds the memory limit
    - Disallow dropping the `AUTO_INCREMENT` attribute of columns in TiDB to avoid misoperations. To drop this attribute, change the `tidb_allow_remove_auto_inc` system variable
- Fixed issues
    - Fix the issue that the uncommented TiDB-specific syntax `PRE_SPLIT_REGIONS` might cause errors in the downstream database during data replication
    - Fix the issue in TiDB that the slow query logs are incorrect when getting the result of `PREPARE` + `EXECUTE` by using the cursor
    - Fix the issue in PD that adjacent small Regions cannot be merged
    - Fix the issue in TiKV that file descriptor leak in idle clusters might cause TiKV processes to exit abnormally when the processes run for a long time
- Contributors

    Our thanks go to the following contributors from the community for helping this release:

    - [sduzh](https://github.com/sduzh)
    - [lizhenda](https://github.com/lizhenda)
