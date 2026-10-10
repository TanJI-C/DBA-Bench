# TiDB 3.1.1 release notes: new features and bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.1.1.md`
- Source Title: `TiDB 3.1.1 Release Notes`
- Source Heading Path: `TiDB 3.1.1 Release Notes | TiDB 3.1.1 Release Notes > New Features | TiDB 3.1.1 Release Notes > Bug Fixes`
- Source Line Ranges: `5-49`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `br`
- Topic Tags: `release-notes`, `new-features`, `bug-fixes`, `sql`, `parser`, `auto-random`, `grafana`, `delta-tree`, `isolation-read`, `partition-selection`, `nested-query`, `recover-table`, `flashback-table`, `upgrade`, `backup-restore`, `data-loss-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0138_a62f816f6b`
- Source ID: `tidb-docs-8.1:releases/release-3.1.1.md#tidb-3-1-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `00915fb8a68ca61145bbc3f24dd360287381d4e8254c3c692ac68b90710efc31`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.1.1#tidb-3-1-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 3.1.1 release notes that summarize new features and bug fixes across TiDB, TiFlash, and BR.
- Retrieval Keywords: TiDB 3.1.1 Release Notes, release date April 30, 2020, TiDB version 3.1.1, TiDB Ansible version 3.1.1, auto_rand_base, Feature ID comment, registered statement fragment, TiFlash DeltaTree engine Grafana, cache the handle and version columns, decimal data encoding in the Chunk codec, reduce open file descriptors, isolation read setting at the instance level does not take effect, partition (P0), UPDATE SQL statement only queries from a view, wrong results caused by removing the not not from the nested query, recover table, flashback table, potential data loss issue when renaming a table, TiFlash fails to start normally after upgrade, special characters, BR restores a table with the auto_random attribute, duplicate entry error
- Follow-up Guidance: The chunk also points to the related pull requests and BR issue for several listed fixes and features.
- Classification Note: This is a self-managed release-notes chunk because the official content is the TiDB 3.1.1 release notes covering new features and bug fixes for shared, TiDB, TiFlash, and BR components.

## Official Source Content

# TiDB 3.1.1 Release Notes

Release date: April 30, 2020

TiDB version: 3.1.1

TiDB Ansible version: 3.1.1
## New Features

+ TiDB

    - Add the table option for `auto_rand_base` [#16812](https://github.com/pingcap/tidb/pull/16812)
    - Add the `Feature ID` comment: In the special comments of SQL statements, only the registered statement fragment can be parsed by the parser; otherwise, the statement is ignored [#16155](https://github.com/pingcap/tidb/pull/16155)

+ TiFlash

    - Cache the `handle` and `version` columns to reduce the disk I/O for a single read request
    - Add in Grafana the graphics related to the read and write workloads of DeltaTree engine
    - Optimize the decimal data encoding in the `Chunk` codec
    - Reduce the number of open file descriptors when TiFlash is in low workload
## Bug Fixes

+ TiDB

    - Fix the issue that the isolation read setting at the instance level does not take effect, and that the isolation read setting is incorrectly retained after TiDB is upgraded [#16482](https://github.com/pingcap/tidb/pull/16482) [#16802](https://github.com/pingcap/tidb/pull/16802)
    - Fix the partition selection syntax on the hash partitioned table so that an error is not reported for syntaxes such as `partition (P0)` [#16076](https://github.com/pingcap/tidb/pull/16076)
    - Fix the issue that when an `UPDATE` SQL statement only queries from a view but does not update the view, the update statement still reports an error [#16789](https://github.com/pingcap/tidb/pull/16789)
    - Fix the issue of wrong results caused by removing the `not not` from the nested query [#16423](https://github.com/pingcap/tidb/pull/16423)

+ TiFlash

    - Fix the issue that an error occurs when reading data from a Region that is in the abnormal state
    - Modify the mapping of table names in TiFlash to correctly support `recover table`/`flashback table`
    - Modify the storage path to fix the potential data loss issue that occurs when renaming a table
    - Modify the read mode in the online update scenario to improve the read performance
    - Fix the issue that TiFlash fails to start normally after upgrade if the database/table name contains special characters

+ Tools

    - Backup & Restore (BR)

        * Fix the issue that after BR restores a table with the `auto_random` attribute, inserting data might trigger the duplicate entry error [#241](https://github.com/pingcap/br/issues/241)
