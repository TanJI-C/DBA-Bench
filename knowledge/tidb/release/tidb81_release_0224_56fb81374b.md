# Bug fixes for TiFlash and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.1.0.md`
- Source Title: `TiDB 5.1 Release Notes`
- Source Heading Path: `TiDB 5.1 Release Notes > Bug Fixes`
- Source Line Ranges: `309-352`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiflash`, `lightning`, `br`, `ticdc`
- Topic Tags: `bug-fixes`, `mpp`, `restore`, `import`, `replication`, `sorter`, `metrics`, `memory-control`, `gc-safe-point`, `flow-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0224_56fb81374b`
- Source ID: `tidb-docs-8.1:releases/release-5.1.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cafe417bee4f2f68f761168c475f65326ec82494271b434cd8a0287616b3075b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.1.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.1 bug fixes for TiFlash or tools such as TiDB Lightning, BR, and TiCDC, especially around casting correctness, MPP task handling, restore or import failures, replication interruption, Unified Sorter, metrics, memory overflow, or GC safe point blocking.
- Retrieval Keywords: TiFlash incorrect results casting time type to integer type, receiver cannot find corresponding tasks within 10 seconds, invalid iterators in cancelMPPQuery, bitwise operator behavior is different from that of TiDB, overlapping ranges prefix key, incorrect results casting string type to integer type, consecutive and fast writes might make TiFlash out of memory, null pointer during the table GC, writing data to dropped tables panic, TiFlash might panic during BR restore, incorrect results when cloning shared delta index concurrently, Compaction Filter feature enabled panic, TiFlash cannot resolve the lock fallen back from async commit, TIMEZONE type contains the TIMESTAMP type, Segment Split panic, TiDB Lightning panic when generating KV data, batch split Region fails due to the total key size exceeding the raft entry limit, importing CSV files last line does not contain line break characters, auto-increment column of the double type auto_increment value becomes abnormal, backup interruption caused by the failure of a few TiKV nodes, Unified Sorter concurrency issue, MinIO redundant directories interrupt replication, explicit_defaults_for_timestamp, incorrect handling of io.EOF might cause replication interruption, TiKV CDC endpoint CPU metric, defaultBufferChanSize, time zone information is lost in the Avro output, cleaning up stale temporary files in Unified Sorter, forbid sharing the sort-dir directory, deadlock bug in the KV client when many stale Regions exist, --cert-allowed-cn flag, sink flow control, replication task might stop when moving a table, TiKV GC safe point is blocked due to the stagnation of TiCDC changefeed checkpoint
- Follow-up Guidance: This chunk also covers tool-specific fixes in TiDB Lightning, BR, and TiCDC, including Unified Sorter cleanup, `sort-dir` restrictions, `defaultBufferChanSize`, sink flow control, Avro time zone handling, and TiKV GC safe point blocking by a stalled changefeed checkpoint.
- Classification Note: The official content is a release-notes bug-fix section for self-managed TiFlash and related tools, focused on correctness, panic and memory issues, restore and import behavior, and replication stability.

## Official Source Content

- Fix the issue of incorrect results when casting the time type to the integer type
    - Fix a bug that the `receiver` cannot find corresponding tasks within 10 seconds
    - Fix the issue that there might be invalid iterators in `cancelMPPQuery`
    - Fix a bug that the behavior of the `bitwise` operator is different from that of TiDB
    - Fix the alert issue caused by overlapping ranges when using the `prefix key`
    - Fix the issue of incorrect results when casting the string type to the integer type
    - Fix the issue that consecutive and fast writes might make TiFlash out of memory
    - Fix the potential issue that the exception of null pointer might be raised during the table GC
    - Fix the TiFlash panic issue that occurs when writing data to dropped tables
    - Fix the issue that TiFlash might panic during BR restore
    - Fix the issue of incorrect results when cloning shared delta index concurrently
    - Fix the potential panic that occurs when the Compaction Filter feature is enabled
    - Fix the issue that TiFlash cannot resolve the lock fallen back from async commit
    - Fix the issue of incorrect results returned when the casted result of the `TIMEZONE` type contains the `TIMESTAMP` type
    - Fix the TiFlash panic issue that occurs during Segment Split

+ Tools

    + TiDB Lightning

        - Fix the issue of TiDB Lightning panic that occurs when generating KV data [#1127](https://github.com/pingcap/br/pull/1127)
        - Fix a bug that the batch split Region fails due to the total key size exceeding the raft entry limit during the data import [#969](https://github.com/pingcap/br/issues/969)
        - Fix the issue that when importing CSV files, if the last line of the file does not contain line break characters (`\r\n`), an error will be reported [#1133](https://github.com/pingcap/br/issues/1133)
        - Fix the issue that if a table to be imported includes an auto-increment column of the double type, the auto_increment value becomes abnormal [#1178](https://github.com/pingcap/br/pull/1178)

    + Backup & Restore (BR)
        - Fix the issue of backup interruption caused by the failure of a few TiKV nodes [#980](https://github.com/pingcap/br/issues/980)

    + TiCDC

        - Fix the concurrency issue in Unified Sorter and filter the unhelpful error messages [#1678](https://github.com/pingcap/tiflow/pull/1678)
        - Fix a bug that the creation of redundant directories might interrupt the replication with MinIO [#1463](https://github.com/pingcap/tiflow/issues/1463)
        - Set the default value of the `explicit_defaults_for_timestamp` session variable to ON to make the MySQL 5.7 downstream keep the same behavior with the upstream TiDB [#1585](https://github.com/pingcap/tiflow/issues/1585)
        - Fix the issue that the incorrect handling of `io.EOF` might cause replication interruption [#1633](https://github.com/pingcap/tiflow/issues/1633)
        - Correct the TiKV CDC endpoint CPU metric in the TiCDC dashboard [#1645](https://github.com/pingcap/tiflow/pull/1645)
        - Increase `defaultBufferChanSize` to avoid replication blocking in some cases [#1259](https://github.com/pingcap/tiflow/issues/1259)
        - Fix the issue that the time zone information is lost in the Avro output [#1712](https://github.com/pingcap/tiflow/pull/1712)
        - Support cleaning up stale temporary files in Unified Sorter and forbid sharing the `sort-dir` directory [#1742](https://github.com/pingcap/tiflow/pull/1742)
        - Fix a deadlock bug in the KV client that occurs when many stale Regions exist [#1599](https://github.com/pingcap/tiflow/issues/1599)
        - Fix the wrong help information in the `--cert-allowed-cn` flag [#1697](https://github.com/pingcap/tiflow/pull/1697)
        - Revert the update for `explicit_defaults_for_timestamp` which requires the SUPER privilege when replicating data to MySQL [#1750](https://github.com/pingcap/tiflow/pull/1750)
        - Support the sink flow control to reduce the risk of memory overflow [#1840](https://github.com/pingcap/tiflow/pull/1840)
        - Fix a bug that the replication task might stop when moving a table [#1828](https://github.com/pingcap/tiflow/pull/1828)
        - Fix the issue that the TiKV GC safe point is blocked due to the stagnation of TiCDC changefeed checkpoint [#1759](https://github.com/pingcap/tiflow/pull/1759)
