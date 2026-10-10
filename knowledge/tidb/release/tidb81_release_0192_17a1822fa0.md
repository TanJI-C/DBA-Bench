# TiDB 4.0.8 bug fixes across components and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.8.md`
- Source Title: `TiDB 4.0.8 Release Notes`
- Source Heading Path: `TiDB 4.0.8 Release Notes > Bug Fixes`
- Source Line Ranges: `93-156`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `lightning`
- Topic Tags: `bug-fixes`, `panic`, `wrong-results`, `data-types`, `replication`, `backup`, `restore`, `gcs`, `multi-disk`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0192_17a1822fa0`
- Source ID: `tidb-docs-8.1:releases/release-4.0.8.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9e266ad8988291f94f2e25850061b39a705ab1efff238c357ac2f3a9d5efdadd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.8#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.8.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB 4.0.8 bug fixes related to panics, wrong results, type conversion issues, replication issues, backup or restore failures, or TiFlash multi-disk deployment problems.
- Retrieval Keywords: TiDB 4.0.8 Bug Fixes, partitioned tables panic, outer join wrong result index merge join, BIT type NULL value returned if data is too long, corrupted default value for the BIT type column, BIT type to INT64 overflow error, propagate column optimization hybrid type column, outdated plans from the plan cache panic, FROM_UNIXTIME and UNION ALL truncated result, Enum type converted to Float wrong results, RegionStore.accessStore panic, BatchPointGet maximum unsigned integer sorting wrong result, Enum and Set coercibilities wrong, YEAR conversion ambiguous, KV duration panel store0 wrong reported result, Float type inserted regardless of out of range error, generated column bad NULL values, invalid auto-id during pessimistic transaction retry, ALTER TABLE change the Enum/Set type constraint is not checked, cop tasks wrong runtime information, duplicate ORDER BY condition sub-optimal execution plans, generated metric profile font size exceeds the maximum allowable value, mutex conflict in encryption causes pd-worker to process heartbeats slowly, failure to back up databases on GCS when the storage class is specified, Key Visualizer of TiDB Dashboard might cause PD panic, PD store is down for more than 10 minutes, multi-disk TiFlash deployment wrong capacity, broken data files after restart, send on closed channel panic during restore, failure to update the GC safepoint, incorrect mod revision cache, wrong column information, retrying to get Region information in the local mode
- Follow-up Guidance: For non-defect changes introduced in the same release, refer to the New Features and Improvements sections of the TiDB 4.0.8 release notes.
- Classification Note: This is classified as bug fixes because the official content lists corrected defects across TiDB, TiKV, PD, TiFlash, BR, TiCDC, and TiDB Lightning, including panics, wrong results, and restore or replication issues.

## Official Source Content

## Bug Fixes

+ TiDB

    - Fix the unexpected panic that occurs when using partitioned tables [#20565](https://github.com/pingcap/tidb/pull/20565)
    - Fix the wrong result of outer join when filtering the outer side using index merge join [#20427](https://github.com/pingcap/tidb/pull/20427)
    - Fix the issue that the `NULL` value is returned when converting data to the `BIT` type if the data is too long [#20363](https://github.com/pingcap/tidb/pull/20363)
    - Fix the corrupted default value for the `BIT` type column [#20340](https://github.com/pingcap/tidb/pull/20340)
    - Fix the overflow error that might occur when converting the `BIT` type to the `INT64` type [#20312](https://github.com/pingcap/tidb/pull/20312)
    - Fix the possible wrong result of the propagate column optimization for the hybrid type column [#20297](https://github.com/pingcap/tidb/pull/20297)
    - Fix the panic that might occur when storing outdated plans from the plan cache [#20246](https://github.com/pingcap/tidb/pull/20246)
    - Fix the bug that the returned result is mistakenly truncated if `FROM_UNIXTIME` and `UNION ALL` are used together [#20240](https://github.com/pingcap/tidb/pull/20240)
    - Fix the issue that wrong results might be returned when the `Enum` type value is converted to the `Float` type [#20235](https://github.com/pingcap/tidb/pull/20235)
    - Fix the possible panic of `RegionStore.accessStore` [#20210](https://github.com/pingcap/tidb/pull/20210)
    - Fix the wrong result returned when sorting the maximum unsigned integer in `BatchPointGet` [#20205](https://github.com/pingcap/tidb/pull/20205)
    - Fix the bug that the coercibilities of `Enum` and `Set` are wrong [#20364](https://github.com/pingcap/tidb/pull/20364)
    - Fix an issue of ambiguous `YEAR` conversion [#20292](https://github.com/pingcap/tidb/pull/20292)
    - Fix the issue of wrong reported result that occurs when the **KV duration** panel contains `store0` [#20260](https://github.com/pingcap/tidb/pull/20260)
    - Fix the issue that the `Float` type data is mistakenly inserted regardless of the `out of range` error [#20252](https://github.com/pingcap/tidb/pull/20252)
    - Fix the bug that the generated column does not handle bad `NULL` values [#20216](https://github.com/pingcap/tidb/pull/20216)
    - Fix the inaccurate error information for the `YEAR` type data that is out of range [#20170](https://github.com/pingcap/tidb/pull/20170)
    - Fix the unexpected `invalid auto-id` error that might occur during the pessimistic transaction retry [#20134](https://github.com/pingcap/tidb/pull/20134)
    - Fix the issue that the constraint is not checked when using `ALTER TABLE` to change the `Enum`/`Set` type [#20046](https://github.com/pingcap/tidb/pull/20046)
    - Fix the wrong runtime information of `cop` tasks recorded when multiple operators are used for concurrency [#19947](https://github.com/pingcap/tidb/pull/19947)
    - Fix the issue that read-only system variables cannot be explicitly selected as the session variables [#19944](https://github.com/pingcap/tidb/pull/19944)
    - Fix the issue that the duplicate `ORDER BY` condition might cause sub-optimal execution plans [#20333](https://github.com/pingcap/tidb/pull/20333)
    - Fix the issue that the generated metric profile might fail if the font size exceeds the maximum allowable value [#20637](https://github.com/pingcap/tidb/pull/20637)

+ TiKV

    - Fix the bug that the mutex conflict in encryption causes pd-worker to process heartbeats slowly [#8869](https://github.com/tikv/tikv/pull/8869)
    - Fix the issue that the memory profile is mistakenly generated [#8790](https://github.com/tikv/tikv/pull/8790)
    - Fix the failure to back up databases on GCS when the storage class is specified [#8763](https://github.com/tikv/tikv/pull/8763)
    - Fix the bug that a learner cannot find a leader when the Region is restarted or newly split [#8864](https://github.com/tikv/tikv/pull/8864)

+ PD

    - Fix a bug that Key Visualizer of TiDB Dashboard might cause PD panic in some cases [#3096](https://github.com/pingcap/pd/pull/3096)
    - Fix the bug that PD might panic if a PD store is down for more than 10 minutes [#3069](https://github.com/pingcap/pd/pull/3069)

+ TiFlash

    - Fix the issue of wrong timestamp in the log message
    - Fix the issue that during the multi-disk TiFlash deployment, the wrong capacity causes the creation of TiFlash replicas to fail
    - Fix the bug that TiFlash might throw errors about broken data files after restart
    - Fix the issue that broken files might be left on disk after TiFlash crashes
    - Fix the bug that it might take a long time to wait for index during learner reads if the proxy cannot catch up with the latest Raft lease information
    - Fix the bug that the proxy writes too much Region state information to the key-value engine while replaying the outdated Raft log

+ Tools

    + Backup and Restore (BR)

        - Fix the `send on closed channel` panic during restore [#559](https://github.com/pingcap/br/pull/559)

    + TiCDC

        - Fix the unexpected exit caused by the failure to update the GC safepoint [#979](https://github.com/pingcap/tiflow/pull/979)
        - Fix the issue that the task status is unexpectedly flushed because of the incorrect mod revision cache [#1017](https://github.com/pingcap/tiflow/pull/1017)

    + TiDB Lightning

        - Fix the issue of wrong column information [#420](https://github.com/pingcap/tidb-lightning/pull/420)
        - Fix the infinity loop that occurs when retrying to get Region information in the local mode [#418](https://github.com/pingcap/tidb-lightning/pull/418)
