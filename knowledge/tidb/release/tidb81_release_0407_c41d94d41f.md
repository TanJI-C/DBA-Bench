# Bug fixes for TiCDC, DM, Lightning, and TiDB Binlog

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.6.md`
- Source Title: `TiDB 6.5.6 Release Notes`
- Source Heading Path: `TiDB 6.5.6 Release Notes > Bug fixes`
- Source Line Ranges: `153-181`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `ticdc`, `dm`, `lightning`, `tikv`, `pd`, `tidb`
- Topic Tags: `bug-fixes`, `replication`, `ddl`, `redo-log`, `replication-lag`, `object-storage`, `pd-scaling`, `oom`, `schema-tracking`, `optimistic-mode`, `data-import`, `physical-import`, `binlog`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0407_c41d94d41f`
- Source ID: `tidb-docs-8.1:releases/release-6.5.6.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7a2fc1a9fd41d4bdff20f55ab6c1fd363c282f0034da0c7f03965b50820535ab`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.6 bug fixes affecting TiCDC, DM, TiDB Lightning, or TiDB Binlog around replication, DDL handling, redo log, object storage, import failures, or Drainer behavior.
- Retrieval Keywords: TiDB 6.5.6 Bug fixes, TiCDC lossy DDL panic, #9739, RESUME redo log enabled error, #9769, replication lag longer when TiKV node crashes, #9741, WHERE statement does not use the primary key when replicating to TiDB or MySQL, #9988, workload not distributed evenly across TiCDC nodes, #9839, interval between replicating DDL statements is too long when redo log is enabled, #9960, changefeed cannot replicate DML events in bidirectional replication mode if the target table is dropped and then recreated in upstream, #10079, replication lag becomes longer due to too many NFS files when replicating data to an object storage service, #10041, TiCDC server panic when replicating data to an object storage service, #10137, TiCDC accesses the invalid old address during PD scaling up and down, #9584, fetching wrong memory information might cause OOM issues, #9762, DM skips partition DDLs in optimistic mode, #9788, DM cannot properly track upstream table schemas when skipping online DDLs, #9587, replication lag returned by DM keeps growing when a failed DDL is skipped and no subsequent DDLs are executed, #9605, DM skips all DMLs when resuming a task in optimistic mode, #9588, write to tikv with no leader returned, #45673, HTTP retry requests do not use the current request content, #47930, TiDB Lightning gets stuck during writeToTiKV, #46321, remove unnecessary get_regions calls in physical import mode, #45507, Drainer exits when transporting a transaction greater than 1 GB, #28659
- Follow-up Guidance: 
- Classification Note: This chunk is a release-note bug-fix summary for self-managed TiDB 6.5.6 covering multiple shared components: TiCDC, DM, TiDB Lightning, and TiDB Binlog.

## Official Source Content

- Fix the issue that TiCDC server might panic when executing lossy DDL statements in upstream [#9739](https://github.com/pingcap/tiflow/issues/9739) @[hicqu](https://github.com/hicqu)
        - Fix the issue that the replication task reports an error when executing `RESUME` with the redo log feature enabled [#9769](https://github.com/pingcap/tiflow/issues/9769) @[hicqu](https://github.com/hicqu)
        - Fix the issue that replication lag becomes longer when the TiKV node crashes [#9741](https://github.com/pingcap/tiflow/issues/9741) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that the `WHERE` statement does not use the primary key as the condition when replicating data to TiDB or MySQL [#9988](https://github.com/pingcap/tiflow/issues/9988) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that the workload of a replication task is not distributed evenly across TiCDC nodes [#9839](https://github.com/pingcap/tiflow/issues/9839) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that the interval between replicating DDL statements is too long when redo log is enabled [#9960](https://github.com/pingcap/tiflow/issues/9960) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that the changefeed cannot replicate DML events in bidirectional replication mode if the target table is dropped and then recreated in upstream [#10079](https://github.com/pingcap/tiflow/issues/10079) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that the replication lag becomes longer due to too many NFS files when replicating data to an object storage service [#10041](https://github.com/pingcap/tiflow/issues/10041) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that the TiCDC server might panic when replicating data to an object storage service [#10137](https://github.com/pingcap/tiflow/issues/10137) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that TiCDC accesses the invalid old address during PD scaling up and down [#9584](https://github.com/pingcap/tiflow/issues/9584) @[fubinzh](https://github.com/fubinzh) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that fetching wrong memory information might cause OOM issues in some operating systems [#9762](https://github.com/pingcap/tiflow/issues/9762) @[sdojjy](https://github.com/sdojjy)

    + TiDB Data Migration (DM)

        - Fix the issue that DM skips partition DDLs in optimistic mode [#9788](https://github.com/pingcap/tiflow/issues/9788) @[GMHDBJD](https://github.com/GMHDBJD)
        - Fix the issue that DM cannot properly track upstream table schemas when skipping online DDLs [#9587](https://github.com/pingcap/tiflow/issues/9587) @[GMHDBJD](https://github.com/GMHDBJD)
        - Fix the issue that replication lag returned by DM keeps growing when a failed DDL is skipped and no subsequent DDLs are executed [#9605](https://github.com/pingcap/tiflow/issues/9605) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that DM skips all DMLs when resuming a task in optimistic mode [#9588](https://github.com/pingcap/tiflow/issues/9588) @[GMHDBJD](https://github.com/GMHDBJD)

    + TiDB Lightning

        - Fix the issue that data import fails when encountering the `write to tikv with no leader returned` error [#45673](https://github.com/pingcap/tidb/issues/45673) @[lance6716](https://github.com/lance6716)
        - Fix the issue that data import fails because HTTP retry requests do not use the current request content [#47930](https://github.com/pingcap/tidb/issues/47930) @[lance6716](https://github.com/lance6716)
        - Fix the issue that TiDB Lightning gets stuck during `writeToTiKV` [#46321](https://github.com/pingcap/tidb/issues/46321) @[lance6716](https://github.com/lance6716)
        - Remove unnecessary `get_regions` calls in physical import mode [#45507](https://github.com/pingcap/tidb/issues/45507) @[mittalrishabh](https://github.com/mittalrishabh)

    + TiDB Binlog

        - Fix the issue that Drainer exits when transporting a transaction greater than 1 GB [#28659](https://github.com/pingcap/tidb/issues/28659) @[jackysp](https://github.com/jackysp)
