# Bug fixes for DM and TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.3.2.md`
- Source Title: `TiDB 5.3.2 Release Notes`
- Source Heading Path: `TiDB 5.3.2 Release Notes > Bug Fixes`
- Source Line Ranges: `152-163`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dm`, `lightning`
- Topic Tags: `bug fixes`, `replication`, `relay log`, `gtid`, `disk usage`, `panic`, `import`, `precheck`, `checksum`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0266_275a6dab05`
- Source ID: `tidb-docs-8.1:releases/release-5.3.2.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7d1cf13d4102d506e15ae60461e9fb4e60879b9f9470c67f1c16ff2714aa480d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.3.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.3.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.3.2 bug fixes in DM or TiDB Lightning involving relay log behavior, GTID-related CPU and logging issues, replication of uppercase tables, worker panic conditions, import precheck coverage, or checksum and auto_increment import failures.
- Retrieval Keywords: TiDB 5.3.2 Bug Fixes, DM, TiDB Lightning, occupies more disk space after the task automatically resumes, uppercase table cannot be replicated, case-sensitive: true, filtered DDL in the downstream, task resumption failure, DM worker panic, SHOW CREATE TABLE, primary key is not first in the index, CPU usage may increase, large amount of log is printed, GTID is enabled, relay log may be disabled after the DM-master reboots, Local-backend import failure, out-of-bounds data, auto_increment column, precheck does not check local disk resources and cluster availability, checksum error, GC life time is shorter than transaction duration
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release-note bug-fix summary because it lists fixes in TiDB Data Migration (DM) and TiDB Lightning for TiDB 5.3.2.

## Official Source Content

- Fix the issue that DM occupies more disk space after the task automatically resumes [#3734](https://github.com/pingcap/tiflow/issues/3734) [#5344](https://github.com/pingcap/tiflow/issues/5344)
        - Fix an issue that the uppercase table cannot be replicated when `case-sensitive: true` is not set [#5255](https://github.com/pingcap/tiflow/issues/5255)
        - Fix the issue that in some cases manually executing the filtered DDL in the downstream might cause task resumption failure [#5272](https://github.com/pingcap/tiflow/issues/5272)
        - Fix the DM worker panic issue that occurs when the primary key is not first in the index returned by the `SHOW CREATE TABLE` statement [#5159](https://github.com/pingcap/tiflow/issues/5159)
        - Fix the issue that CPU usage may increase and a large amount of log is printed when GTID is enabled or when the task is automatically resumed [#5063](https://github.com/pingcap/tiflow/issues/5063)
        - Fix the issue that the relay log may be disabled after the DM-master reboots [#4803](https://github.com/pingcap/tiflow/issues/4803)

    + TiDB Lightning

        - Fix the issue of Local-backend import failure caused by out-of-bounds data in the `auto_increment` column [#27937](https://github.com/pingcap/tidb/issues/27937)
        - Fix the issue that the precheck does not check local disk resources and cluster availability [#34213](https://github.com/pingcap/tidb/issues/34213)
        - Fix the checksum error "GC life time is shorter than transaction duration" [#32733](https://github.com/pingcap/tidb/issues/32733)
