# Bug fixes across TiDB, TiKV, PD, TiFlash, BR, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.15.md`
- Source Title: `TiDB 4.0.15 Release Notes`
- Source Heading Path: `TiDB 4.0.15 Release Notes > Bug fixes`
- Source Line Ranges: `85-140`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`
- Topic Tags: `release-notes`, `bug-fixes`, `collation`, `restore`, `disk-full`, `panic`, `data-inconsistency`, `oom`, `memory-leak`, `ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0175_dd2804247f`
- Source ID: `tidb-docs-8.1:releases/release-4.0.15.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `60b89aeae35c73db04aec242cdafe12181fee889c409b96fad3b6ab0c5b76f73`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.15#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.15.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 4.0.15 bug fixes involving TiDB, TiKV, PD, TiFlash, BR, or TiCDC, especially for specific errors, panics, OOM issues, data inconsistency, or DDL-related fixes.
- Retrieval Keywords: TiDB 4.0.15 Bug fixes, collation is incorrectly set for binary literals when building ranges, #23672, index out of range GROUP BY UNION, #26553, TiDB might fail to send requests if TiKV has tombstone stores, #23676, #24648, /debug/sub-optimal-plan HTTP API removed, #27264, wrong character set and collation for the case when expression, #26662, file already exists error when TDE is enabled during data restore, #1179, potential disk full issue caused by corrupted snapshot files, #10813, TiKV deletes stale Regions too frequently, #10680, TiKV frequently reconnects the PD client, #9690, encryption file dictionary stale file information, #9115, PD does not fix the down peers in time, #4077, PD might panic when scaling out TiKV, #3868, TiFlash data inconsistency when deployed on multiple disks, TiFlash incorrect results CONSTANT < <= > >= COLUMN, TiFlash store size in metrics is inaccurate under heavy writing, TiFlash cannot restore data when deployed on multiple disks, TiFlash cannot garbage-collect the delta data after running for a long time, average speed is inaccurately calculated for backup and restore, #1405, ErrSchemaStorageTableMiss, #2422, ErrGCTTLExceeded, #2391, capture list outdated capture, #2388, TiCDC processor deadlock, #2017, multiple processors might write data to the same table when this table is being re-scheduled, #2230, EtcdWorker snapshot isolation is violated, #2557, changefeed cannot be stopped due to the DDL sink error, #2552, TiCDC Open Protocol outputs an empty value when there is no change in a transaction, #2612, panic on the unsigned TINYINT type, #2648, Decrease the gRPC window size to avoid the OOM that occurs when TiCDC captures too many Regions, #2202, Fix the OOM issue that occurs when TiCDC captures too many Regions, #2673, process panic when encoding mysql.TypeString mysql.TypeVarString mysql.TypeVarchar into JSON, #2758, memory leak issue when creating a new changefeed, #2389, DDL handling fails when a changefeed starts at the finish TS of a schema change, #2603, potential DDL loss when the owner crashes when executing DDL statements, #1260, insecure concurrent access to the map in SinkManager, #2298
- Follow-up Guidance: The same release notes file also contains Compatibility changes, Feature enhancement, and Improvements for TiDB 4.0.15.
- Classification Note: This chunk is classified as release bug fixes because it lists corrected errors and stability issues across multiple components, including specific named errors, panic cases, OOM fixes, and data consistency fixes.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix a bug that collation is incorrectly set for binary literals when building ranges [#23672](https://github.com/pingcap/tidb/issues/23672)

    - Fix the "index out of range" error that occurs when a query includes both `GROUP BY` and `UNION` [#26553](https://github.com/pingcap/tidb/pull/26553)
    - Fix the issue that TiDB might fail to send requests if TiKV has tombstone stores [#23676](https://github.com/pingcap/tidb/issues/23676) [#24648](https://github.com/pingcap/tidb/issues/24648)
    - Remove the undocumented `/debug/sub-optimal-plan` HTTP API [#27264](https://github.com/pingcap/tidb/pull/27264)
    - Fix the issue of wrong character set and collation for the `case when` expression [#26662](https://github.com/pingcap/tidb/issues/26662)

+ TiKV

    - Fix the issue that BR reports the "file already exists" error when TDE is enabled during data restore [#1179](https://github.com/pingcap/br/issues/1179)
    - Fix the potential disk full issue caused by corrupted snapshot files [#10813](https://github.com/tikv/tikv/issues/10813)
    - Fix the issue that TiKV deletes stale Regions too frequently [#10680](https://github.com/tikv/tikv/issues/10680)
    - Fix the issue that TiKV frequently reconnects the PD client [#9690](https://github.com/tikv/tikv/issues/9690)
    - Check stale file information from the encryption file dictionary [#9115](https://github.com/tikv/tikv/issues/9115)

+ PD

    - Fix the issue that PD does not fix the down peers in time [#4077](https://github.com/tikv/pd/issues/4077)
    - Fix a bug that PD might panic when scaling out TiKV [#3868](https://github.com/tikv/pd/issues/3868)

+ TiFlash

    - Fix the potential issue of data inconsistency that occurs when TiFlash is deployed on multiple disks
    - Fix a bug of incorrect results that occurs when queries contain filters like `CONSTANT`, `<`, `<=`, `>`, `>=`, or `COLUMN`
    - Fix the issue that the store size in metrics is inaccurate under heavy writing
    - Fix a potential bug that TiFlash cannot restore data when deployed on multiple disks
    - Fix the potential issue that TiFlash cannot garbage-collect the delta data after running for a long time

+ Tools

    + Backup & Restore (BR)

        - Fix a bug that the average speed is inaccurately calculated for backup and restore [#1405](https://github.com/pingcap/br/issues/1405)

    + TiCDC

        - Fix the `ErrSchemaStorageTableMiss` error that occurs when the DDL Job duplication is encountered in the integrated test [#2422](https://github.com/pingcap/tiflow/issues/2422)
        - Fix a bug that a changefeed cannot be removed if the `ErrGCTTLExceeded` error occurs [#2391](https://github.com/pingcap/tiflow/issues/2391)
        - Fix the issue that outdated capture might appear in the output of the `capture list` command [#2388](https://github.com/pingcap/tiflow/issues/2388)
        - Fix the deadlock issue in the TiCDC processor [#2017](https://github.com/pingcap/tiflow/pull/2017)
        - Fix a data inconsistency issue that occurs because multiple processors might write data to the same table when this table is being re-scheduled [#2230](https://github.com/pingcap/tiflow/issues/2230)
        - Fix a bug that the `EtcdWorker` snapshot isolation is violated in metadata management [#2557](https://github.com/pingcap/tiflow/pull/2557)
        - Fix the issue that the changefeed cannot be stopped due to the DDL sink error [#2552](https://github.com/pingcap/tiflow/issues/2552)
        - Fix the issue of TiCDC Open Protocol: TiCDC outputs an empty value when there is no change in a transaction [#2612](https://github.com/pingcap/tiflow/issues/2612)
        - Fix a bug that causes TiCDC to panic on the unsigned `TINYINT` type [#2648](https://github.com/pingcap/tiflow/issues/2648)
        - Decrease the gRPC window size to avoid the OOM that occurs when TiCDC captures too many Regions [#2202](https://github.com/pingcap/tiflow/issues/2202)
        - Fix the OOM issue that occurs when TiCDC captures too many Regions [#2673](https://github.com/pingcap/tiflow/issues/2673)
        - Fix the issue of process panic that occurs when encoding the data types such as `mysql.TypeString, mysql.TypeVarString, mysql.TypeVarchar` into JSON [#2758](https://github.com/pingcap/tiflow/issues/2758)
        - Fix the a memory leak issue that might occur when creating a new changefeed [#2389](https://github.com/pingcap/tiflow/issues/2389)
        - Fix a bug that DDL handling fails when a changefeed starts at the finish TS of a schema change [#2603](https://github.com/pingcap/tiflow/issues/2603)
        - Fix the issue of potential DDL loss when the owner crashes when executing DDL statements [#1260](https://github.com/pingcap/tiflow/issues/1260)
        - Fix the issue of insecure concurrent access to the map in `SinkManager` [#2298](https://github.com/pingcap/tiflow/pull/2298)
