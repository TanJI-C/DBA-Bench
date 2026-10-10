# Bug fixes for BR, TiCDC, and DM

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.2.md`
- Source Title: `TiDB 8.1.2 Release Notes`
- Source Heading Path: `TiDB 8.1.2 Release Notes > Bug fixes`
- Source Line Ranges: `139-159`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `ticdc`, `dm`, `tidb`
- Topic Tags: `bug fixes`, `backup`, `restore`, `pitr`, `cdc`, `monitoring`, `ddl`, `redo`, `leader election`, `data inconsistency`, `security`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0609_93be03c0b0`
- Source ID: `tidb-docs-8.1:releases/release-8.1.2.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9cab5955a43e5fc2e16dbbd6d8d95e1e4b83bce127375d0ec8b6cc5d77f40cea`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 8.1.2 bug fixes in BR, TiCDC, or DM involving backup and PITR errors, monitoring inaccuracies, DDL handling, redo error reporting, span replication during Region splits, or DM leader election inconsistency.
- Retrieval Keywords: TiDB 8.1.2 bug fixes, BR logs encrypted information, snapshot backups based on AWS EBS fail during the preparation phase, backup gets stuck, checkpoint path of backup and restore incompatible with some external storage, k8s.io/api library version, PITR Information schema is out of date, large number of tables in the cluster but the actual data size is small, TiCDC Resolved TS latency monitoring Puller module incorrect values, enable-table-across-nodes, Span replication tasks lost during Region splits, redo module fails to properly report errors, TiCDC mistakenly discards DDL tasks, schema versions of DDL tasks become non-incremental, TiDB DDL owner changes, barrier-ts monitoring metric, changefeed checkpoints inaccurate, DM-master nodes simultaneously become leaders, data inconsistency
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release note bug-fix summary for self-managed tools in TiDB 8.1.2, specifically BR, TiCDC, and DM.

## Official Source Content

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that logs might print out encrypted information [#57585](https://github.com/pingcap/tidb/issues/57585) @[kennytm](https://github.com/kennytm)
        - Fix the issue that snapshot backups based on AWS EBS might fail during the preparation phase, causing the backup to get stuck [#52049](https://github.com/pingcap/tidb/issues/52049) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that the checkpoint path of backup and restore is incompatible with some external storage [#55265](https://github.com/pingcap/tidb/issues/55265) @[Leavrth](https://github.com/Leavrth)
        - Fix potential security vulnerabilities by upgrading the `k8s.io/api` library version [#57790](https://github.com/pingcap/tidb/issues/57790) @[BornChanger](https://github.com/BornChanger)
        - Fix the issue that PITR tasks might return the `Information schema is out of date` error when there are a large number of tables in the cluster but the actual data size is small [#57743](https://github.com/pingcap/tidb/issues/57743) @[Tristan1900](https://github.com/Tristan1900)

    + TiCDC

        - Fix the issue that the Resolved TS latency monitoring in the Puller module displays incorrect values [#11561](https://github.com/pingcap/tiflow/issues/11561) @[wlwilliamx](https://github.com/wlwilliamx)
        - Fix the issue that when `enable-table-across-nodes` is enabled, some Span replication tasks for a table might be lost during Region splits [#11675](https://github.com/pingcap/tiflow/issues/11675) @[wk989898](https://github.com/wk989898)
        - Fix the issue that the redo module fails to properly report errors [#11744](https://github.com/pingcap/tiflow/issues/11744) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that TiCDC mistakenly discards DDL tasks when the schema versions of DDL tasks become non-incremental during TiDB DDL owner changes [#11714](https://github.com/pingcap/tiflow/issues/11714) @[wlwilliamx](https://github.com/wlwilliamx)
        - Fix the issue that the **barrier-ts** monitoring metric for changefeed checkpoints might be inaccurate  [#11553](https://github.com/pingcap/tiflow/issues/11553) @[3AceShowHand](https://github.com/3AceShowHand)

    + TiDB Data Migration (DM)

        - Fix the issue that multiple DM-master nodes might simultaneously become leaders, leading to data inconsistency [#11602](https://github.com/pingcap/tiflow/issues/11602) @[GMHDBJD](https://github.com/GMHDBJD)
