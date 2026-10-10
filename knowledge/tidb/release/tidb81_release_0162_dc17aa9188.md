# Bug fixes for PD, TiFlash, TiCDC, BR, and TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.11.md`
- Source Title: `TiDB 4.0.11 Release Notes`
- Source Heading Path: `TiDB 4.0.11 Release Notes > Bug Fixes`
- Source Line Ranges: `132-170`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tiflash`, `ticdc`, `br`, `lightning`, `tikv`
- Topic Tags: `bug-fixes`, `metrics`, `store-management`, `data-loss`, `crash`, `changefeed`, `restore`, `import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0162_dc17aa9188`
- Source ID: `tidb-docs-8.1:releases/release-4.0.11.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f852365ced6653f670591af2138c171cd70d0de4d2850e10cee1f7d973728f04`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.11#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.11.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.11 bug fixes across PD, TiFlash, TiCDC, BR, or TiDB Lightning involving metrics display, tombstone store handling, store limit persistence, scatter range scheduler limits, crashes, data loss, changefeed behavior, restore issues, or import errors.
- Retrieval Keywords: TiDB 4.0.11 Bug Fixes, PD member health metrics incorrectly displayed, tombstone store still has peers, store limit cannot be persisted, scatter range scheduler limit constriction, TiFlash min max decimal wrong, TiFlash might crash when reading data, data written after DDL operations might be lost after data compaction, TiFlash incorrectly handles decimal constants in Coprocessor, potential crash during learner read process, division by 0 or NULL between TiDB and TiFlash, TiCDC ErrTaskStatusNotExists capture session unexpectedly exit, changefeed affected by another changefeed old value switch, invalid sort-engine parameter hang, debugging information on non-owner nodes panic, ticdc_processor_num_of_tables, ticdc_processor_table_resolved_ts, potential data loss if a processor crashes when adding a table, abnormal TiCDC server exits during table migrations, service GC safepoint is lost, KV client might skip creating the event feed, atomicity of transactions is broken when replicated to the downstream, BR restores the backup big Region, BR restores a table's Auto ID even if the table does not have Auto ID, TiDB Lightning column count mismatch TiDB-backend, TiDB-backend panics if the column count of the source file and the column count of the target table mismatch, TiKV unexpectedly panic during TiDB Lightning data import
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release note because it lists bug fixes in TiDB 4.0.11 for multiple components including PD, TiFlash, TiCDC, BR, and TiDB Lightning.

## Official Source Content

- Fix the issue that member health metrics are incorrectly displayed [#3368](https://github.com/pingcap/pd/pull/3368)
    - Forbid removing the tombstone store that still has peers [#3352](https://github.com/pingcap/pd/pull/3352)
    - Fix the issue that the store limit cannot be persisted [#3403](https://github.com/pingcap/pd/pull/3403)
    - Fix the limit constriction of the scatter range scheduler [#3401](https://github.com/pingcap/pd/pull/3401)

+ TiFlash

    - Fix a bug that the `min`/`max` result is wrong for the decimal type
    - Fix a bug that TiFlash might crash when reading data
    - Fix the issue that some data written after DDL operations might be lost after data compaction
    - Fix the issue that TiFlash incorrectly handles decimal constants in Coprocessor
    - Fix the potential crash during the learner read process
    - Fix the inconsistent behaviors of division by `0` or `NULL` between TiDB and TiFlash

+ Tools

    + TiCDC

        - Fix a bug that the TiCDC service might unexpectedly exit when `ErrTaskStatusNotExists` and the closing of `capture` session occur at the same time [#1240](https://github.com/pingcap/tiflow/pull/1240)
        - Fix the old value switch issue that a `changefeed` might be affected by another `changefeed` [#1347](https://github.com/pingcap/tiflow/pull/1347)
        - Fix a bug that the TiCDC service might hang when processing a new `changefeed` with the invalid `sort-engine` parameter [#1309](https://github.com/pingcap/tiflow/pull/1309)
        - Fix the issue of panic that occurs when getting the debugging information on non-owner nodes [#1349](https://github.com/pingcap/tiflow/pull/1349)
        - Fix the issue that the `ticdc_processor_num_of_tables` and `ticdc_processor_table_resolved_ts` metrics are not properly updated when adding or removing tables [#1351](https://github.com/pingcap/tiflow/pull/1351)
        - Fix the issue of potential data loss if a processor crashes when adding a table [#1363](https://github.com/pingcap/tiflow/pull/1363)
        - Fix a bug that the owner might lead to abnormal TiCDC server exits during table migrations [#1352](https://github.com/pingcap/tiflow/pull/1352)
        - Fix a bug that TiCDC does not exit in time after the service GC safepoint is lost [#1367](https://github.com/pingcap/tiflow/pull/1367)
        - Fix a bug that the KV client might skip creating the event feed [#1336](https://github.com/pingcap/tiflow/pull/1336)
        - Fix a bug that the atomicity of transactions is broken when the transactions are replicated to the downstream [#1375](https://github.com/pingcap/tiflow/pull/1375)

    + Backup & Restore (BR)

        - Fix the issue that TiKV might be caused to generate a big Region after BR restores the backup [#702](https://github.com/pingcap/br/pull/702)
        - Fix the issue that BR restores a table's Auto ID even if the table does not have Auto ID [#720](https://github.com/pingcap/br/pull/720)

    + TiDB Lightning

        - Fix a bug that `column count mismatch` might be triggered when using the TiDB-backend [#535](https://github.com/pingcap/tidb-lightning/pull/535)
        - Fix a bug that TiDB-backend panics if the column count of the source file and the column count of the target table mismatch [#528](https://github.com/pingcap/tidb-lightning/pull/528)
        - Fix a bug that TiKV might unexpectedly panic during TiDB Lightning's data import [#554](https://github.com/pingcap/tidb-lightning/pull/554)
