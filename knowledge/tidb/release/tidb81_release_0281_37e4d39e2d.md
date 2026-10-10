# Bug fixes for DM

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.4.1.md`
- Source Title: `TiDB 5.4.1 Release Notes`
- Source Heading Path: `TiDB 5.4.1 Release Notes > Bug Fixes`
- Source Line Ranges: `167-173`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `bug-fixes`, `dm`, `replication`, `checkpoint`, `ddl`, `query-status`, `panic`, `gtid`, `logging`, `cpu-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0281_37e4d39e2d`
- Source ID: `tidb-docs-8.1:releases/release-5.4.1.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `612fcb427eade7b190b1fae4039ac7272b96626e004e06d83fa9e5599167cccb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.4.1#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.4.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.4.1 DM bug fixes related to checkpoint logging, slow replication, safemode update panic, filtered DDL resumption failure, query-status output, SHOW CREATE TABLE index order panic, or increased CPU usage with GTID.
- Retrieval Keywords: TiDB 5.4.1 DM bug fixes, checkpoint has no change skip sync flush checkpoint, replication is very slow, Column length too big, execution errors of the update statement in safemode may cause the DM-worker panic, manually executing the filtered DDL in the downstream might cause task resumption failure, query-status command no data returned when binlog is not enabled in the upstream, DM worker panic primary key is not first in the index, SHOW CREATE TABLE statement, CPU usage may increase and a large amount of log is printed when GTID is enabled, task is automatically resumed
- Follow-up Guidance: The source lists these items under TiDB Data Migration (DM) in the TiDB 5.4.1 Bug Fixes section.
- Classification Note: This is a release-note bug-fix summary chunk specifically for the DM component in self-managed TiDB 5.4.1.

## Official Source Content

- Fix the issue that hundreds of "checkpoint has no change, skip sync flush checkpoint" print in the log and the replication is very slow [#4619](https://github.com/pingcap/tiflow/issues/4619)
        - Fix a bug that long varchars report an error `Column length too big` [#4637](https://github.com/pingcap/tiflow/issues/4637)
        - Fix the issue that execution errors of the update statement in safemode may cause the DM-worker panic [#4317](https://github.com/pingcap/tiflow/issues/4317)
        - Fix the issue that in some cases manually executing the filtered DDL in the downstream might cause task resumption failure [#5272](https://github.com/pingcap/tiflow/issues/5272)
        - Fix a bug that no data is returned for the `query-status` command when binlog is not enabled in the upstream [#5121](https://github.com/pingcap/tiflow/issues/5121)
        - Fix the DM worker panic issue that occurs when the primary key is not first in the index returned by the `SHOW CREATE TABLE` statement [#5159](https://github.com/pingcap/tiflow/issues/5159)
        - Fix the issue that CPU usage may increase and a large amount of log is printed when GTID is enabled or when the task is automatically resumed [#5063](https://github.com/pingcap/tiflow/issues/5063)
